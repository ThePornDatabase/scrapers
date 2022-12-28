import re
import json
import html
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDirtyAuditionsSpider(BaseSceneScraper):
    name = 'DirtyAuditions'
    network = 'Dirty Auditions'
    parent = 'Dirty Auditions'
    site = 'Dirty Auditions'

    start_urls = [
        'https://dirtyauditions.com',
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
        'pagination': '/scenes?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        jsoncode = response.xpath('//script[contains(@id, "NEXT_DATA")]/text()')
        if jsoncode:
            jsondata = json.loads(jsoncode.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = SceneItem()
                item['title'] = html.unescape(scene['title'])
                item['id'] = scene['id']
                item['description'] = html.unescape(re.sub('<[^<]+?>', '', scene['description']))
                if scene['thumb']:
                    item['image'] = scene['thumb']
                elif scene['trailer_screencap']:
                    item['image'] = scene['trailer_screencap']
                elif scene['extra_thumbnails']:
                    item['image'] = scene['extra_thumbnails']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = scene['trailer_url']
                scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).isoformat()
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').isoformat()
                item['url'] = f"https://dirtyauditions.com/videos/{scene['slug']}"
                item['tags'] = scene['tags']
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['site'] = 'Dirty Auditions'
                item['parent'] = 'Dirty Auditions'
                item['network'] = 'Dirty Auditions'
                item['performers'] = []
                for model in scene['models_slugs']:
                    item['performers'].append(model['name'])

                if item['id'] and item['title']:
                    days = int(self.days)
                    if days > 27375:
                        filterdate = "0000-00-00"
                    else:
                        filterdate = date.today() - timedelta(days)
                        filterdate = filterdate.strftime('%Y-%m-%d')

                    if self.debug:
                        if not item['date'] > filterdate:
                            item['filtered'] = "Scene filtered due to date restraint"
                        print(item)
                    else:
                        if filterdate:
                            if item['date'] > filterdate:
                                yield item
                        else:
                            yield item
