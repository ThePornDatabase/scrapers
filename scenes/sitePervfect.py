import string
import json
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePervfectSpider(BaseSceneScraper):
    name = 'Pervfect'
    network = ''
    parent = ''
    site = ''

    start_urls = [
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):
        performers = requests.get("http://www.pervfect.net/api/v1/performers?limit=500&offset=0&status=active&sort=sort&order=1&keyword=&sex=&size=")
        if performers:
            performers = json.loads(performers.content)
            performer_list = []
            for performer in performers:
                performer_list.append({'id': performer['_id'], 'name': performer['name']})

        url = "http://www.pervfect.net/api/v1/videos?keyword=&limit=500&offset=0&order=1&performer=&sort=sort&type=recent"
        yield scrapy.Request(url, callback=self.get_scenes,
                             meta={'page': self.page, 'performer_list': performer_list},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        performer_list = response.meta['performer_list']
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()
            item['title'] = string.capwords(scene['name'].strip())
            item['description'] = scene['description'].strip()
            item['date'] = self.parse_date(scene['createdAt']).isoformat()
            item['id'] = scene['_id']
            item['url'] = f"http://www.pervfect.net/movies/{scene['alias']}/{scene['_id']}/"
            item['image'] = self.format_link(response, scene['imageFullPath']).replace(" ", "%20")
            item['image_blob'] = ''
            item['trailer'] = self.format_link(response, scene['fileTrailerPath']).replace(" ", "%20")
            item['tags'] = []
            if "tags" in scene and scene['tags']:
                for tag in scene['tags']:
                    item['tags'].append(string.capwords(tag.strip()))
            if "categoriesInfo" in scene and scene['categoriesInfo']:
                for category in scene['categoriesInfo']:
                    item['tags'].append(string.capwords(category['name']))

            item['performers'] = []
            if 'performer' in scene and scene['performer']:
                for performer in scene['performer']:
                    for performer_item in performer_list:
                        if performer_item['id'] == performer:
                            item['performers'].append(string.capwords(performer_item['name']))
            item['site'] = "Pervfect"
            item['parent'] = "Pervfect"
            item['network'] = "Pervfect"
            yield item
