import re
import html
import string
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteInkedVixensXXXSpider(BaseSceneScraper):
    name = 'InkedVixensXXX'

    start_urls = [
        'https://www.inkedvixensxxx.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/movies?page=%s&per_page=20',
        'type': 'Scene',
    }

    def start_requests(self):
        tagdata = []
        for i in range(1, 10):
            req = requests.get(f'https://inkedvixensxxx.com/wp-json/wp/v2/movie_tags?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                jsondata = re.search(r'(\[.*\])', req.text).group(1)
                tagtemp = json.loads(jsondata)
                tagdata = tagdata + tagtemp
            else:
                break

        catdata = []
        for i in range(1, 10):
            req = requests.get(f'https://inkedvixensxxx.com/wp-json/wp/v2/movie_categories?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                tagtemp = []
                jsondata = re.search(r'(\[.*\])', req.text).group(1)
                tagtemp = json.loads(jsondata)
                catdata = catdata + tagtemp
            else:
                break

        modeldata = []
        for i in range(1, 10):
            req = requests.get(f'https://inkedvixensxxx.com/wp-json/wp/v2/models?per_page=100&page={str(i)}')
            if req and len(req.text) > 5:
                modeltemp = []
                jsondata = re.search(r'(\[.*\])', req.text).group(1)
                modeltemp = json.loads(jsondata)
                modeldata = modeldata + modeltemp
            else:
                break

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'tagdata': tagdata, 'catdata': catdata, 'modeldata': modeldata},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = re.search(r'(\[.*\])', response.text).group(1)
        jsondata = json.loads(jsondata)
        for scene in jsondata:
            item = self.init_scene()

            item['trailer'] = ""

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = string.capwords(unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip()))

            for model_id in scene['models']:
                for model in meta['modeldata']:
                    if model['id'] == model_id:
                        item['performers'].append(string.capwords(model['name']))

            for tag_id in scene['movie_tags']:
                for tag in meta['tagdata']:
                    if tag['id'] == tag_id:
                        item['tags'].append(tag['name'])

            for category in scene['movie_categories']:
                for tag in meta['catdata']:
                    if tag['id'] == category:
                        item['tags'].append(tag['name'])

            item['site'] = 'Inked Vixens XXX'
            item['parent'] = 'Inked Vixens XXX'
            item['network'] = 'Inked Vixens XXX'
            item['url'] = scene['link']

            if 'featured_image_urls' in scene and 'full' in scene['featured_image_urls'] and scene['featured_image_urls']['full']:
                item['image'] = re.sub(r'\?.*', '', scene['featured_image_urls']['full'][0])
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if not item['image_blob'] or len(item['image_blob']) < 2000:
                    item['image'] = ''
                    item['image_blob'] = ''

            yield self.check_item(item, self.days)
