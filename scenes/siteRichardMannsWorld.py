import re
import html
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRichardMannsWorldSpider(BaseSceneScraper):
    name = 'RichardMannsWorld'
    network = "Richard Manns World"
    parent = "Richard Manns World"
    site = "Richard Manns World"

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://richardmannsworld.com',
    ]

    headers = {
        'age_gate': '18',
        'wpml_browser_redirect_test': '0',
    }

    selector_map = {
        'performers': '//span[@itemprop="actors"]/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/index.php/wp-json/wp/v2/posts?page=%s&per_page=10'
    }

    def get_scenes(self, response):

        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        jsondata = json.loads(response.text)
        for scene in jsondata:
            meta = response.meta
            meta['id'] = scene['id']
            meta['url'] = scene['link']
            meta['date'] = scene['date']
            meta['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())

            meta['image'] = ''
            meta['image_blob'] = ''
            link = f"https://richardmannsworld.com/wp-json/wp/v2/media?parent={meta['id']}"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                imagelist = json.loads(req.text)
                for image in imagelist:
                    if "player" in image['title']['rendered'] or ("player" in image['source_url'] and ".jpg" in image['source_url']):
                        meta['image'] = image['source_url']
                        meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            meta['description'] = scene['content']['rendered']
            if meta['description']:
                meta['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', meta['description'])).replace("\n", " ").strip())
                if 'vc_raw_html' in meta['description']:
                    meta['description'] = ''

            tags = []
            link = f"https://richardmannsworld.com/wp-json/wp/v2/categories?post={meta['id']}"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                taglist = []
                taglist = json.loads(req.text)
                for tag in taglist:
                    tags.append(tag['name'])
            meta['tags'] = tags

            yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)
