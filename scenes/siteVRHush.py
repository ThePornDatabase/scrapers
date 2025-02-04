import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRHushSpider(BaseSceneScraper):
    name = 'VRHush'
    network = 'VR Hush'
    parent = 'VR Hush'
    site = 'VR Hush'

    start_urls = [
        'https://vrhush.com',
    ]

    selector_map = {
        'title': '//h1[@class="latest-scene-title"]/text()',
        'description': '//span[contains(@class,"full-description")]/text()',
        'date': '//div[contains(@class,"latest-scene-meta-1")]/div[1]/text()',
        'date_formats': ['%b %d, %y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h5/a[contains(@href, "/models/")]/text()',
        'tags': '//p[@class="tag-container"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'scenes/(.*?)_',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
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
                item['image'] = scene['trailer_screencap']
                if item['image'][:2] == '//':
                    item['image'] = "https:" + item['image']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = ""
                scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).strftime('%Y-%m-%d')
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').strftime('%Y-%m-%d')
                item['url'] = f"https://www.vrhush.com/scenes/{scene['slug']}"
                item['tags'] = scene['tags']
                try:
                    duration = str(int(float(scene['videos_duration'])))
                    item['duration'] = duration
                except:
                    item['duration'] = ''
                item['site'] = 'VR Hush'
                item['parent'] = 'VR Hush'
                item['network'] = 'VR Hush'
                item['performers'] = []
                for model in scene['models_slugs']:
                    item['performers'].append(model['name'])

                yield self.check_item(item, self.days)
