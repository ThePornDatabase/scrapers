import re
import unidecode
import json
import html
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteShockChallengeSpider(BaseSceneScraper):
    name = 'ShockChallenge'
    network = 'ShockChallenge'
    parent = 'ShockChallenge'
    site = 'ShockChallenge'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://www.shockchallenge.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/posts?page=%s&per_page=20'
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://www.shockchallenge.com/wp-json/wp/v2/tags?per_page=100&page={str(i)}')
            if req and len(req.text) > 1:
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

            desc_block = scene['excerpt']['rendered']
            desc_block = html.unescape(desc_block)
            desc_block = desc_block.replace("\\", "")

            image = scene['jetpack_featured_media_url']
            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', desc_block)).strip())

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = string.capwords(unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip()))
            for model_id in scene['tags']:
                for tag in meta['tagdata']:
                    if tag['id'] == model_id:
                        if " " in tag['name']:
                            item['performers'].append(tag['name'])
                        else:
                            item['performers'].append(tag['name'] + " " + str(tag['id']))

            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
            item['tags'] = ['Bondage', 'Electro Sex']
            item['site'] = 'Shock Challenge'
            item['parent'] = 'Shock Challenge'
            item['network'] = 'Shock Challenge'
            item['url'] = scene['link']

            yield self.check_item(item, self.days)
