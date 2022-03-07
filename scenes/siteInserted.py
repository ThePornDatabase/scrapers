import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteInsertedSpider(BaseSceneScraper):
    name = 'Inserted'
    network = 'Inserted'
    parent = 'Inserted'
    site = 'Inserted'

    start_urls = [
        'https://inserted.com',
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
        'pagination': '/tour/videos?page=%s'
    }

    def get_scenes(self, response):
        jsoncode = response.xpath('//script[contains(text(), "window.__DATA__")]/text()')
        if jsoncode:
            jsoncode = re.search(r'({.*})\s+window', jsoncode.get()).group(1)
            jsondata = json.loads(jsoncode)
            jsondata = jsondata['videos']['items']
            for scene in jsondata:
                item = SceneItem()
                item['title'] = scene['title']
                item['id'] = scene['id']
                item['description'] = re.sub('<[^<]+?>', '', scene['description'])
                item['image'] = scene['trailer']['poster']
                item['image_blob'] = None
                item['trailer'] = scene['trailer']['src']
                scene_date = self.parse_date(scene['release_date']).isoformat()
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').isoformat()
                short_url = item['title'].lower().replace(" ", "-")
                item['url'] = f"https://inserted.com/tour/videos/{item['id']}/{short_url}"
                item['tags'] = []
                item['site'] = 'Inserted'
                item['parent'] = 'Inserted'
                item['network'] = 'Inserted'
                item['performers'] = []
                for model in scene['models']:
                    item['performers'].append(model['name'])
                if item['title'] and item['id']:
                    yield item
