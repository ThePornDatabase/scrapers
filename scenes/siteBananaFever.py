import re
import html
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBananaFeverSpider(BaseSceneScraper):
    name = 'BananaFever'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://bananafever.com',
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
        'pagination': '/index.php/wp-json/wp/v2/portfolio?page=%s&per_page=10'
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://bananafever.com//index.php//wp-json//wp//v2//portfolio_category?per_page=100&page={str(i)}')
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
            if 'wp:featuredmedia' in scene['_links']:
                image_url = scene['_links']['wp:featuredmedia'][0]['href']
            else:
                image_url = ""
            item['id'] = str(scene['id'])
            item['date'] = scene['date']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            item['tags'] = ['Asian', 'Interracial']
            item['trailer'] = None
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['excerpt']['rendered'])).strip())
            if 'vc_raw_html' in item['description']:
                item['description'] = ''
            item['performers'] = []
            for category in scene['portfolio_category']:
                if '105' not in str(category) and '106' not in str(category) and '170' not in str(category) and '163' not in str(category):
                    for tag in meta['tagdata']:
                        if tag['id'] == category:
                            item['performers'].append(tag['name'])
            item['site'] = 'Banana Fever'
            item['parent'] = 'Banana Fever'
            item['network'] = 'Banana Fever'
            item['url'] = scene['link']

            meta['item'] = item

            if image_url:
                req = requests.get(image_url)
                if req and len(req.text) > 5:
                    imagerow = json.loads(req.text)
                else:
                    imagerow = None

                item['image'] = imagerow['guid']['rendered']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None

            if " - Demo" not in item['title']:
                yield item
