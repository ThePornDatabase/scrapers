import re
import html
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKailaniKaiSpider(BaseSceneScraper):
    name = 'KailaniKai'

    start_urls = [
        'https://www.kailanikaixxx.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php/wp-json/wp/v2/posts?page=%s&per_page=20',
        'type': 'Scene',
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://kailanikaixxx.com/index.php/wp-json/wp/v2/tags?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                tagtemp = json.loads(req.text)
                tagdata = tagdata + tagtemp
            else:
                break

        catdata = []
        for i in range(1, 10):
            req = requests.get(f'https://kailanikaixxx.com/index.php/wp-json/wp/v2/categories?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                tagtemp = json.loads(req.text)
                catdata = catdata + tagtemp
            else:
                break

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'tagdata': tagdata, 'catdata': catdata},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = self.init_scene()

            desc_block = scene['content']['rendered']
            desc_block = html.unescape(desc_block)
            desc_block = desc_block.replace("\\", "")

            item['trailer'] = ""

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            item['title'] = re.sub(r'[^a-zA-Z0-9 \-&]', '', item['title'].replace("FRESH & NEW!", "").replace("NEW!", "")).strip()
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['excerpt']['rendered'])).strip())
            if "Please purchase" in item['description'] or "To purchase" in item['description']:
                item['description'] = ''
            item['performers'] = ['Kailani Kai']
            for tag_id in scene['tags']:
                for tag in meta['tagdata']:
                    if tag['id'] == tag_id:
                        item['tags'].append(tag['name'])

            cat = []
            categories = scene['categories']
            for category in scene['categories']:
                for tag in meta['catdata']:
                    if tag['id'] == category:
                        cat.append(tag['name'])

            # ~ if "Paid Per Post" in cat or "Videos" in cat:
            if "Paid Per Post" in cat:
                item['site'] = 'Kailani Kai XXX'
                item['parent'] = 'Kailani Kai XXX'
                item['network'] = 'Kailani Kai XXX'
                item['url'] = scene['link']

                imageurl = scene['_links']['wp:featuredmedia'][0]['href']
                meta['item'] = item.copy()
                yield scrapy.Request(imageurl, callback=self.get_scene_image, meta=meta)

    def get_scene_image(self, response):
        meta = response.meta
        item = meta['item']
        jsondata = json.loads(response.text)
        image = jsondata['guid']['rendered']
        item['image'] = image
        item['image_blob'] = self.get_image_blob_from_link(image)
        yield self.check_item(item, self.days)
