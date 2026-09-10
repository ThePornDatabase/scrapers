import re
import string
import json
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteInsertedSpider(BaseSceneScraper):
    name = 'CosplayXGirls'
    network = 'CosplayXGirls'
    parent = 'CosplayXGirls'
    site = 'CosplayXGirls'

    start_urls = [
        'https://cosplayxgirls.com',
    ]

    selector_map = {
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
                item = self.init_scene()
                item['title'] = scene['title']
                item['id'] = scene['id']
                item['description'] = re.sub('<[^<]+?>', '', scene['description'])
                if scene['trailer_screencap']:
                    item['image'] = scene['trailer_screencap']
                else:
                    item['image'] = scene['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['image'] = item['image'].replace(' ', '%20')
                item['trailer'] = scene['trailer_url']
                scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).isoformat()
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').strftime('%Y-%m-%d')
                item['url'] = f"https://CosplayXGirls.com/videos/{scene['slug']}"
                item['tags'] = scene['tags']
                item['tags'].append("Cosplay")
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['site'] = 'CosplayXGirls'
                item['parent'] = 'CosplayXGirls'
                item['network'] = 'CosplayXGirls'
                item['performers_data'] = []
                for model in scene['models_thumbs']:
                    perf = {}
                    perf['extra'] = {}
                    perf['extra']['gender'] = "Female"
                    perf['name'] = string.capwords(model['name'])
                    perf['image'] = model['thumb'].replace(" ", "%20")
                    perf['image_blob'] = self.get_image_blob_from_link(model['thumb'])
                    perf['site'] = "CosplayXGirls"
                    perf['network'] = "CosplayXGirls"
                    item['performers_data'].append(perf)
                    item['performers'].append(string.capwords(model['name']))

                if self.check_item(item, self.days):
                    yield item
