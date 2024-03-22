import json
import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSexSelectorSpider(BaseSceneScraper):
    name = 'SexSelector'
    network = 'Bang Bros'
    parent = 'Sex Selector'
    site = 'Sex Selector'

    start_urls = [
        # 'https://www.sexselector.com',  Moved into Project1Service scraper
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'.*videos/(.*)',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            scenes = jsondata['props']['pageProps']['shoots']
            screens = jsondata['props']['pageProps']['shootScenes']
            for scene in scenes:
                item = SceneItem()
                item['title'] = scene['title']
                item['description'] = scene['description']
                item['date'] = scene['publishDate']
                item['performers'] = []
                for model in scene['model']:
                    item['performers'].append(string.capwords(model['name']))
                item['tags'] = []
                for tag in scene['tag']:
                    item['tags'].append(string.capwords(tag['name']))
                item['id'] = scene['id']
                # ~ item['url'] = 'https://www.sexselector.com/video/' + str(item['id']) + "/" + item['title'].lower().replace(" ", "-")
                slug = re.sub(r"[^a-zA-Z0-9 -]", "", item['title'].lower()).replace(" ", "-")
                item['url'] = 'https://www.sexselector.com/video/' + str(item['id']) + "/" + slug
                item['trailer'] = ''
                item['network'] = 'Bang Bros'
                item['parent'] = 'Sex Selector'
                item['site'] = 'Sex Selector'
                uuid = scene['gameId']
                guid = (list(screens[uuid].keys())[0])
                image = ''
                image = screens[uuid][guid]['thumbnail']
                if image:
                    item['image'] = self.format_link(response, image)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image_blob'] = ''

                yield self.check_item(item, self.days)
