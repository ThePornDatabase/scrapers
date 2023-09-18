import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBravoFuckerSpider(BaseSceneScraper):
    name = 'BravoFucker'
    network = 'Bravo Fucker'
    parent = 'Bravo Fucker'
    site = 'Bravo Fucker'

    start_urls = [
        'https://www.bravofucker.com',
    ]

    selector_map = {
        'external_id': '',
        'pagination': '/en/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsondata = response.xpath('//script[contains(@type,"ld+json")]/text()').get()
        jsondata = json.loads(jsondata, strict=False)
        for scene in jsondata['itemListElement']:
            scene = scene['item']
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['name'])
            item['description'] = self.cleanup_description(scene['description'])
            item['date'] = scene['datePublished']
            item['image'] = scene['thumbnailUrl']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['url'] = scene['url']
            item['id'] = re.search(r'detail/(\d+)', item['url']).group(1)
            item['trailer'] = ''
            item['tags'] = ['Gay Porn']
            item['performers'] = []
            item['type'] = "Scene"
            item['site'] = "Bravo Fucker"
            item['parent'] = "Bravo Fucker"
            item['network'] = "Bravo Fucker"
            yield self.check_item(item, self.days)
