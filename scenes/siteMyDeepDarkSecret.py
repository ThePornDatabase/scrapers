import re
import json
import html
import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMyDeepDarkSecretJSONSpider(BaseSceneScraper):
    name = 'MyDeepDarkSecret'
    network = 'My Deep Dark Secret'
    parent = 'My Deep Dark Secret'
    site = 'My Deep Dark Secret'

    start_urls = [
        'https://mydeepdarksecret.com',
    ]


    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': "//article/div[@class='entry-content']//div[contains(@class,'et_section_regular')]//div[contains(@class,'et_pb_row_1-4_3-4')]//div[contains(@class,'et_pb_column_3_4')]//div[contains(@class,'et_pb_text')]/text()",
        'performers': '//div[contains(@class, "et_pb_text_align_left")]/ul/li[contains(., "Models")]/a/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '',
        'external_id': 'project/([a-z0-9-_]+)/?',
        'trailer': '',
        'pagination': 'https://mydeepdarksecret.com/wp-json/wp/v2/posts?per_page=10&page=%s'
    }


    def get_scenes(self, response):
        responsedata = re.sub(r'<[^<]+?>', '', response.text)
        meta = response.meta
        categories =[{"id": 11, "name": "Asian Girls"}, {"id": 6, "name": "Barely Legal Porn"}, {"id": 15, "name": "Big Boobs"}, {"id": 9, "name": "Big Butt"}, {"id": 13, "name": "Black Girls"}, {"id": 2, "name": "Interracial Anal"}, {"id": 1, "name": "Interracial Creampies"}, {"id": 4, "name": "Interracial MILF Porn"}, {"id": 3, "name": "Interracial Orgy"}, {"id": 5, "name": "Interracial Porn"}]
        jsondata = json.loads(responsedata)
        for scene in jsondata:
            item = SceneItem()
            image_url = scene['_links']['wp:featuredmedia'][0]['href']
            item['id'] = str(scene['slug'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = self.clean_text(scene['title']['rendered'])
            item['trailer'] = None
            item['description'] = self.clean_text(scene['excerpt']['rendered'])
            if 'vc_raw_html' in item['description']:
                item['description'] = ''
            item['performers'] = []
            item['tags'] = []
            for tag in scene['categories']:
                for category in categories:
                    if str(category['id']) == str(tag):
                        item['tags'].append(category['name'])
            item['site'] = 'My Deep Dark Secret'
            item['parent'] = 'My Deep Dark Secret'
            item['network'] = 'My Deep Dark Secret'
            item['url'] = scene['link']

            meta['item'] = item
            yield scrapy.Request(image_url, callback=self.get_image_link, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image_link(self, response):
        responsedata = re.sub(r'<[^<]+?>', '', response.text)
        item = response.meta['item']
        jsondata = json.loads(responsedata)

        item['image'] = jsondata['guid']['rendered']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        yield self.check_item(item, self.days)

    def clean_text(self, text):
        text = unidecode.unidecode(text)
        text = html.unescape(text).strip()
        text = unidecode.unidecode(text)
        text = re.sub(r'<[^<]+?>', '', text)
        return text
