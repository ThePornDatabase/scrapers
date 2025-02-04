import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteInsertedSpider(BaseSceneScraper):
    name = 'PassionPOV'
    network = 'PassionPOV'
    parent = 'PassionPOV'
    site = 'PassionPOV'

    start_urls = [
        'https://passionpov.com',
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
        'pagination': '/videos?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        jsoncode = response.xpath('//script[contains(@id, "NEXT_DATA")]/text()')
        if jsoncode:
            jsondata = json.loads(jsoncode.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = SceneItem()
                item['title'] = scene['title']
                item['id'] = scene['id']
                item['description'] = re.sub('<[^<]+?>', '', scene['description'])
                item['image'] = scene['trailer_screencap']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = scene['trailer_url']
                scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).isoformat()
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').strftime('%Y-%m-%d')
                item['url'] = f"https://passionpov.com/videos/{scene['slug']}"
                item['tags'] = scene['tags']
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['site'] = 'PassionPOV'
                item['parent'] = 'PassionPOV'
                item['network'] = 'PassionPOV'
                item['performers'] = []
                for model in scene['models_slugs']:
                    item['performers'].append(model['name'])

                yield self.check_item(item, self.days)
