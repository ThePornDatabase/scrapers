import re
import os
import json
import time
import base64
import hashlib
import slugify
import scrapy
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTrailerTrashBoysSpider(BaseSceneScraper):
    name = 'TrailerTrashBoys'
    site = 'Trailer Trash Boys'
    parent = 'Trailer Trash Boys'
    network = 'Trailer Trash Boys'

    start_urls = [
        'https://ns-api.nakedsword.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/frontend/scenes/feed?page=%s&sort_by=newest&studios_id=23348',
        'type': 'Scene',
    }

    # The API rejects anything without a valid X-Ident header, answering
    # {"error":"Bad Whitelabel Identification","code":403}.  That header is a
    # base64'd AES-CBC blob of {date, propertyId} keyed with PBKDF2-SHA512.
    #
    # This used to be produced by spawning helpers/TrailerTrashBoys_Token/main.js,
    # an express server on port 3000, via
    #     subprocess.Popen('node helpers/TrailerTrashBoys_Token/main.js')
    # which never worked: Popen was given a single string with no shell=True, so it
    # looked for a binary literally named "node helpers/...main.js" and raised
    # FileNotFoundError; the path was also relative to the working directory, and
    # nothing waited for the server to come up before the token was requested.
    # The same token is generated here directly, with no node, port or subprocess.
    IDENT_PASSPHRASE = '4238e#5a7bfc9209X894890e073a3&&12ea8+b@c'
    IDENT_PROPERTY_ID = '30'

    def make_ident(self):
        plain = json.dumps({'date': int(time.time() * 1000),
                            'propertyId': self.IDENT_PROPERTY_ID}).encode('utf-8')
        salt = os.urandom(256)
        iv = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha512', self.IDENT_PASSPHRASE.encode('utf-8'), salt, 999, dklen=32)
        pad = 16 - (len(plain) % 16)
        encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
        ciphertext = encryptor.update(plain + bytes([pad]) * pad) + encryptor.finalize()
        blob = json.dumps({'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                           'salt': salt.hex(), 'iv': iv.hex()})
        return base64.b64encode(blob.encode('utf-8')).decode('utf-8')

    def api_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'application/json',
            'X-Ident': self.make_ident(),
        }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        link = "https://www.trailertrashboys.com"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = self.copy_meta(response)
        headers = self.api_headers()

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=headers)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))

                # each page needs a fresh X-Ident; the token carries a timestamp
                headers = self.api_headers()

                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=headers)

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['data']['scenes']
        for scene in jsondata:
            item = self.init_scene()

            if "streaming_movie" in scene and scene['streaming_movie']:
                scene2 = scene['streaming_movie']
                orig_id = scene2['id']
                index = scene['index']
                item['id'] = f"{scene2['id']}-{index}"
                if scene['movie']['title'] == scene2['title']:
                    item['title'] = f"{scene2['title']} - Scene {index}"
                else:
                    item['title'] = scene2['title']
                item['description'] = scene2['description']
                item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publish_start']).group(1)
                item['duration'] = self.duration_to_seconds(scene2['runTime'])

                item['image'] = scene['cover_images'][0]['url']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['performers'] = []
                if "stars" in scene and scene['stars']:
                    for star in scene['stars']:
                        item['performers'].append(star['name'])

                item['tags'] = ["Gay"]

                item['trailer'] = scene['sample_video']

                item['site'] = "Trailer Trash Boys"
                item['parent'] = "Trailer Trash Boys"
                item['network'] = "Trailer Trash Boys"

                item['url'] = f"https://www.trailertrashboys.com/movies/{orig_id}/{slugify.slugify(item['title'])}/scene/{index}"
                yield self.check_item(item, self.days)
