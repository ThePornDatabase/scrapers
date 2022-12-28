import string
import json
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJadeKinkSpider(BaseSceneScraper):
    name = 'JadeKink'
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
        url = "https://api.jadekink.com/user/assets/videos/search?limit=500&offset=0"
        yield scrapy.Request(url, callback=self.get_scenes, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['data']['data']
        # ~ print(jsondata)
        # ~ jsonload = jsondata[0]
        # ~ print(jsonload)
        for scene in jsondata:
            item = SceneItem()
            item['title'] = string.capwords(scene['title'].strip())
            item['description'] = scene['description'].strip()
            item['date'] = self.parse_date(scene['createdAt']).isoformat()
            item['id'] = scene['_id']
            item['url'] = f"https://jadekink.com/video/{scene['slug']}/"
            item['image'] = self.format_link(response, scene['thumbnail']['url']).replace(" ", "%20")
            item['image_blob'] = ''
            item['trailer'] = self.format_link(response, scene['teaser']['url']).replace(" ", "%20")
            item['tags'] = []
            item['performers'] = ['JadeKink']
            if "duration" in scene['video']:
                item['duration'] = scene['video']['duration']
            else:
                item['duration'] = None
            item['site'] = "JadeKink"
            item['parent'] = "JadeKink"
            item['network'] = "JadeKink"
            item['type'] = 'Scene'
            yield self.check_item(item, self.days)
