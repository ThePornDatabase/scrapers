import re
import html
import string
import json
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOkkulonSpider(BaseSceneScraper):
    name = 'Okkulon'

    start_urls = [
        'https://www.okkulon.com',
    ]

    selector_map = {
        'external_id': r'',
        # ~ 'pagination': '/wp-json/wp/v2/posts?page=%s&per_page=20',
        'pagination': '/wp-json/wp/v2/product?page=%s&per_page=20',
        'type': 'Scene',
    }

    cookies = {"name": "age_gate", "value": "18"}

    def start_requests(self):
        meta = {}
        link = 'https://okkulon.com'
        yield scrapy.Request(link, callback=self.start_requests2, meta=meta, cookies=self.cookies)

    def start_requests2(self, response):
        link = 'https://okkulon.com/wp-json/wp/v2/tags?per_page=100&page=1'
        yield scrapy.Request(link, callback=self.start_requests3, meta=response.meta)

    def start_requests3(self, response):
        if response.text and len(response.text) > 5:
            tagdata = json.loads(response.text)

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

            item['trailer'] = ""

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = string.capwords(unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip()))

            test_title = re.sub(r'[^a-z]+', '', item['title'].lower())
            for tag_id in scene['tags']:
                for tag in meta['tagdata']:
                    if tag['id'] == tag_id:
                        if re.sub(r'[^a-z]+', '', tag['name'].lower()) in test_title:
                            item['performers'].append(string.capwords(tag['name']))
                        else:
                            item['tags'].append(string.capwords(tag['name']))

            item['site'] = 'Okkulon'
            item['parent'] = 'Okkulon'
            item['network'] = 'Okkulon'
            item['url'] = scene['link']

            if 'jetpack_featured_media_url' in scene and scene['jetpack_featured_media_url']:
                item['image'] = re.sub(r'\?.*', '', scene['jetpack_featured_media_url'])
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if not item['image_blob'] or len(item['image_blob']) < 2000:
                    item['image'] = ''
                    item['image_blob'] = ''

            yield self.check_item(item, self.days)
