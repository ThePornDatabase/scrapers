import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteKingBBCSpider(BaseSceneScraper):
    name = 'KingBBC'
    network = 'King BBC'
    parent = 'King BBC'
    site = 'King BBC'

    start_urls = [
        'https://www.kingbbc.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos/page:%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsondata = response.text.replace("\n", "").replace("\r", "").replace("\t", "").strip()
        for x in range(0, 20):
            jsondata = jsondata.replace("  ", " ")
        jsondata = re.search(r'siteData = (\{.*?\})\s+let', jsondata)

        if jsondata:
            jsondata = jsondata.group(1)
            jsondata = jsondata.replace("}, ]", "}]")
            jsondata = re.sub(r'onclick.*?\\\".*?\\\"', '', jsondata)
            jsondata = json.loads(jsondata, strict=False)
            jsondata = jsondata['posts']
            for scene in jsondata:
                item = SceneItem()

                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_description(scene['description'])
                item['performers'] = [scene['model_name']]
                item['image'] = scene['slides'][0]['img']
                if ".gif" in item['image']:
                    item['image'] = scene['img']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                # ~ item['image_blob'] = ''
                if "?" in item['image']:
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
                item['id'] = scene['id']
                item['url'] = scene['buy_video_url']
                item['tags'] = ['BBC']
                item['trailer'] = ''
                item['date'] = ''
                item['site'] = "KingBBC"
                item['parent'] = "KingBBC"
                item['network'] = "KingBBC"
                yield item
