import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLadySoniaSpider(BaseSceneScraper):
    name = 'LadySonia'

    start_urls = [
        'https://tour.lady-sonia.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/scenes?page=%s&order_by=publish_date&sort_by=desc&tag=',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsoncode = response.xpath('//script[contains(@id, "NEXT_DATA")]/text()')
        if jsoncode:
            jsondata = json.loads(jsoncode.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = self.init_scene()

                item['title'] = self.cleanup_title(scene['title'])
                item['id'] = scene['id']
                item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description'])).replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
                item['image'] = scene['trailer_screencap']
                if item['image'][:2] == '//':
                    item['image'] = "https:" + item['image']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = scene['trailer_url']
                scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).strftime('%Y-%m-%d')
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').strftime('%Y-%m-%d')
                item['url'] = f"https://tour.lady-sonia.com/scenes/{scene['slug']}"
                item['tags'] = scene['tags']
                try:
                    duration = str(int(float(scene['seconds_duration'])))
                    item['duration'] = duration
                except:
                    item['duration'] = ''
                item['site'] = 'Lady Sonia'
                item['parent'] = 'Lady Sonia'
                item['network'] = 'Lady Sonia'
                item['performers'] = []
                item['type'] = "Scene"
                for model in scene['models_slugs']:
                    item['performers'].append(self.cleanup_title(model['name']))

                yield self.check_item(item, self.days)
