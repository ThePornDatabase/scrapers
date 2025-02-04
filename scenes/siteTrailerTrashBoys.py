import re
import slugify
import base64
import requests
import subprocess
import scrapy
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

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = "https://www.trailertrashboys.com"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta

        pro = subprocess.Popen('node helpers/TrailerTrashBoys_Token/main.js')
        token = requests.get('http://127.0.0.1:3000/token').text
        pro.kill()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'X-Ident': base64.b64encode(token.encode('utf-8')).decode('utf-8'),
        }

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
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))

                pro = subprocess.Popen('node helpers/TrailerTrashBoys_Token/main.js')
                token = requests.get('http://127.0.0.1:3000/token').text
                pro.kill()

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
                    'X-Ident': base64.b64encode(token.encode('utf-8')).decode('utf-8'),
                }

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
