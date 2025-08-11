import re
import requests
import html
import string
import json
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOkkulonProductSpider(BaseSceneScraper):
    name = 'OkkulonProduct'

    start_urls = [
        'https://www.okkulon.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/product?page=%s&per_page=20',
        'type': 'Scene',
    }

    cookies = {"name": "age_gate", "value": "18"}

    def start_requests(self):
        meta = {}
        link = 'https://okkulon.com'
        yield scrapy.Request(link, callback=self.start_requests2, meta=meta, cookies=self.cookies)

    def start_requests2(self, response):
        link = 'https://okkulon.com/wp-json/wp/v2/product_tag?per_page=100&page=1'
        yield scrapy.Request(link, callback=self.start_requests3, meta=response.meta)

    def start_requests3(self, response):
        meta = response.meta
        if response.text and len(response.text) > 5:
            meta['tagdata'] = json.loads(response.text)
        link = 'https://okkulon.com/wp-json/wp/v2/product_tag?per_page=100&page=2'
        yield scrapy.Request(link, callback=self.start_requests4, meta=response.meta)

    def start_requests4(self, response):
        meta = response.meta
        meta['page'] = self.page

        if response.text and len(response.text) > 5:
            tagdata = json.loads(response.text)

        meta['tagdata'] = meta['tagdata'] + tagdata

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta=meta,
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
            for tag_id in scene['product_tag']:
                for tag in meta['tagdata']:
                    if tag['id'] == tag_id:
                        # ~ if re.sub(r'[^a-z]+', '', tag['name'].lower()) in test_title:
                            # ~ item['performers'].append(string.capwords(tag['name']))
                        # ~ else:
                            item['tags'].append(string.capwords(tag['name']))

            item['site'] = 'Okkulon'
            item['parent'] = 'Okkulon'
            item['network'] = 'Okkulon'
            item['url'] = scene['link']

            if "wp:attachment" in scene['_links'] and scene['_links']['wp:featuredmedia'][0]['href']:
                image_url = scene['_links']['wp:featuredmedia'][0]['href']
            else:
                image_url = None

            item['image'] = None
            item['image_blob'] = None
            reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
            req = requests.get(image_url, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                imagelist = json.loads(req.text)
                item['image'] = imagelist['guid']['rendered']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            yield self.check_item(item, self.days)
