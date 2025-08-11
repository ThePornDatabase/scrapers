import re
import html
import json
import requests
import unidecode
import scrapy
import base64
import random
import os
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from PIL import Image


class SiteHumiliationPOVSpider(BaseSceneScraper):
    name = 'HumiliationPOV'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://www.humiliationpov.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/blog/wp-json/wp/v2/posts?page=%s&per_page=10'
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://www.humiliationpov.com/blog/wp-json/wp/v2/categories?page={str(i)}&per_page=100')
            if req and len(req.text) > 5:
                tagtemp = []
                tagtemp = json.loads(req.text)
                tagdata = tagdata + tagtemp
            else:
                break

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'tagdata': tagdata},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = self.init_scene()

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            image = re.search(r'img src.*?(http.*?uploads\/.*?\.\w{3})', scene['content']['rendered'])
            if image:
                image_url = image.group(1)
                try:
                    item['image'] = image_url
                    im = Image.open(requests.get(image_url, stream=True).raw)
                    im.seek(1)
                    filename = f"screengrab-{str(random.randrange(100,999999999))}.png"
                    im.save(filename)
                    with open(filename, "rb") as image_file:
                        item['image_blob'] = base64.b64encode(image_file.read()).decode('utf-8')
                    os.remove(filename)
                except Exception as e:
                    print(f"Encountered an error with images: {e}")
            else:
                item['image'] = ""
                item['image_blob'] = ""

            item['trailer'] = None
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['excerpt']['rendered'])).strip())
            if 'vc_raw_html' in item['description']:
                item['description'] = ''
            item['performers'] = []
            item['tags'] = []
            for category in scene['categories']:
                for tag in meta['tagdata']:
                    if tag['id'] == category:
                        item['tags'].append(tag['name'])
            item['site'] = 'Humiliation POV'
            item['parent'] = 'Humiliation POV'
            item['network'] = 'Humiliation POV'
            item['url'] = scene['link']
            if re.search(r'(.*?)-\d+-\d+-\d+', item['url']):
                item['url'] = re.search(r'(.*?)-\d+-\d+-\d+', item['url']).group(1)

            yield self.check_item(item, self.days)
