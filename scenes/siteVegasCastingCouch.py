import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteVegasCastingCouchSpider(BaseSceneScraper):
    name = 'VegasCastingCouch'
    network = 'VegasCastingCouch'
    parent = 'VegasCastingCouch'
    site = 'VegasCastingCouch'

    start_urls = [
        'https://www.vegascastingcouch.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/api/v1/videos?keyword=&limit=16&offset=%s&order=1&performer=&sort=sort&type=recent',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://www.vegascastingcouch.com/api/v1/performers?limit=200&offset=0&status=active&sort=sort&order=1&keyword=&sex=&size="
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        meta['performer_list'] = json.loads(response.text)
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        offset = str(int(page) -1)
        return self.format_url(base, self.get_selector_map('pagination') % offset)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()

            item['id'] = scene['_id']
            item['title'] = scene['name']
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['createdAt']).group(1)
            item['description'] = scene['description']
            item['image'] = "https://www.vegascastingcouch.com" + scene['imageFullPath'].replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = "https://www.vegascastingcouch.com" + scene['fileTrailerPath'].replace(" ", "%20")
            item['tags'] = scene['tags']
            item['performers'] = []
            for performer in scene['performer']:
                for model in meta['performer_list']:
                    if performer == model['_id']:
                        if "&" not in model['name']:
                            item['performers'].append(model['name'])
                        else:
                            item['performers'] = model['name'].split("&")
            item['performers'] = list(map(lambda x: x.strip(), item['performers']))
            item['site'] = "Vegas Casting Couch"
            item['parent'] = "Vegas Casting Couch"
            item['network'] = "Vegas Casting Couch"
            item['url'] = f"https://www.vegascastingcouch.com/movies/{scene['alias']}/{item['id']}"
            yield self.check_item(item, self.days)
