import re
import string
import scrapy
import html
import json
import requests
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteClipsMallSpider(BaseSceneScraper):
    name = 'ClipsMall'

    start_urls = [
        'https://clipsmall.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/product?per_page=10&page=%s',
    }

    def start_requests(self):
        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        meta = {}
        meta['page'] = self.page

        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://clipsmall.com/wp-json/wp/v2/product_tag?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                jsondata = re.search(r'(\[.*\])', req.text).group(1)
                tagtemp = json.loads(jsondata)
                tagdata = tagdata + tagtemp
            else:
                break
        meta['product_tag'] = tagdata

        catdata = []
        for i in range(1, 10):
            req = requests.get(f'https://clipsmall.com/wp-json/wp/v2/product_cat?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                jsondata = re.search(r'(\[.*\])', req.text).group(1)
                tagtemp = json.loads(jsondata)
                catdata = catdata + tagtemp
            else:
                break
        meta['product_cat'] = catdata

        berocket_cat = requests.get("https://clipsmall.com/wp-json/wp/v2/berocket_brand?per_page=100&page=1", headers=reqheaders, timeout=10)
        if berocket_cat and len(berocket_cat.text) > 5:
            meta['berocket_cat'] = json.loads(berocket_cat.text)
        else:
            meta['berocket_cat'] = []

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
            if meta['berocket_cat'] and scene['berocket_brand']:
                for product_berocket in scene['berocket_brand']:
                    for berocket in meta['berocket_cat']:
                        if product_berocket == berocket['id']:
                            item['performers'].append(string.capwords(berocket['name']))

            item['tags'] = []
            if meta['product_cat'] and scene['product_cat']:
                for product_cat in scene['product_cat']:
                    for tag in meta['product_cat']:
                        if product_cat == tag['id']:
                            item['tags'].append(tag['name'])

            if meta['product_tag'] and scene['product_tag']:
                for product_tag in scene['product_tag']:
                    for tag in meta['product_tag']:
                        if product_tag == tag['id']:
                            item['tags'].append(tag['name'])

            item['trailer'] = ''
            item['site'] = "ClipsMall"
            item['parent'] = "ClipsMall"
            item['network'] = "ClipsMall"
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
