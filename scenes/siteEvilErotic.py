import re
import scrapy
import html
import json
import requests
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteEvilEroticSpider(BaseSceneScraper):
    name = 'EvilErotic'

    start_urls = [
        'https://evilerotic.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/posts?per_page=10&page=%s',
    }

    def start_requests(self):
        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        meta = {}
        meta['page'] = self.page

        product_tag = requests.get("https://evilerotic.com/wp-json/wp/v2/tags?per_page=100", headers=reqheaders, timeout=10)
        if product_tag and len(product_tag.text) > 5:
            meta['product_tag'] = json.loads(product_tag.text)
        else:
            meta['product_tag'] = []

        product_cat = requests.get("https://evilerotic.com/wp-json/wp/v2/categories?per_page=100", headers=reqheaders, timeout=10)
        if product_cat and len(product_cat.text) > 5:
            meta['product_cat'] = json.loads(product_cat.text)
        else:
            meta['product_cat'] = []

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies, dont_filter=True)

    def get_scenes(self, response):
        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()

            item['id'] = scene['id']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['content']['rendered'])).replace("\n", " ").strip())
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['url'] = scene['link']
            item['performers'] = []
            if meta['product_cat'] and scene['categories']:
                for perf in scene['categories']:
                    for tag in meta['product_cat']:
                        if perf == tag['id']:
                            item['performers'].append(tag['name'])

            item['tags'] = []
            if meta['product_tag'] and scene['tags']:
                for product_cat in scene['tags']:
                    for tag in meta['product_tag']:
                        if product_cat == tag['id'] and product_cat != 30:
                            item['tags'].append(tag['name'])

            item['trailer'] = ''
            item['site'] = "Evil Erotic"
            item['parent'] = "Evil Erotic"
            item['network'] = "Evil Erotic"
            item['type'] = 'Scene'
            meta['item'] = item

            if "wp:attachment" in scene['_links'] and scene['_links']['wp:featuredmedia'][0]['href']:
                image_url = scene['_links']['wp:featuredmedia'][0]['href']
            else:
                image_url = None

            item['image'] = None
            item['image_blob'] = None
            req = requests.get(image_url, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                imagelist = json.loads(req.text)
                item['image'] = imagelist['guid']['rendered']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            yield self.check_item(item, self.days)
