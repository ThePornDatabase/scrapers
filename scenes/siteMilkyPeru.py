import re
import string
import html
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMilkyPeruSpider(BaseSceneScraper):
    name = 'MilkyPeru'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://milkyperu.com',
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
        'pagination': '/index.php/wp-json/wp/v2/posts?page=%s&per_page=20'
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://milkyperu.com/index.php/wp-json/wp/v2/tags?per_page=100&page={str(i)}')
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
            item = SceneItem()

            desc_block = scene['excerpt']['rendered']
            desc_block = html.unescape(desc_block)
            desc_block = desc_block.replace("\\", "")

            image = scene["yoast_head_json"]['og_image'][0]['url']
            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['excerpt']['rendered'])).strip())

            item['trailer'] = ""
            if re.search(r'(http.*?\.mp4) ', item['description']):
                item['trailer'] = re.search(r'(http.*?\.mp4) ', item['description']).group(1)
                item['description'] = re.search(r'http.*?\.mp4 (.*)', item['description']).group(1)

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            item['performers'] = []
            item['tags'] = []
            for model_id in scene['tags']:
                for tag in meta['tagdata']:
                    if tag['id'] == model_id:
                        item['tags'].append(tag['name'])

            matches = ['Porn Movies', 'Baandidas', 'Best Porn', 'Flirt With', 'Hd Peru Videos', 'Hot Peruvian', 'Hottest Latinas', 'Milky', 'Peru', 'Porn']
            for match in matches:
                for tag in item['tags']:
                    if match.lower() in tag.lower():
                        item['tags'].remove(tag)

            item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))

            item['site'] = 'Milky Peru'
            item['parent'] = 'Milky Peru'
            item['network'] = 'Milky Peru'
            item['url'] = scene['link']

            yield self.check_item(item, self.days)
