import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFuckPassVRSpider(BaseSceneScraper):
    name = 'FuckPassVR'
    network = 'FuckPassVR'
    parent = 'FuckPassVR'
    site = 'FuckPassVR'

    start_urls = [
        'https://www.fuckpassvr.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/api/scene?size=24&page=%s&sortBy=newest&type=grid'
    }

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsonrows = jsondata['data']['scenes']['data']
        for jsondata in jsonrows:
            scene = f"https://www.fuckpassvr.com/api/api/scene/show?slug={jsondata['slug']}&view=0"
            yield scrapy.Request(scene, callback=self.parse_scene)

    def parse_scene(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['data']['scene']
        item = SceneItem()

        item['title'] = jsondata['title'].replace("\r", "").replace("\n", " ").replace("  ", " ")
        item['description'] = re.sub(r'<.*?>', '', jsondata['description']).replace("\r", "").replace("\n", " ").replace("  ", " ")
        item['date'] = jsondata['created_at']
        item['image'] = jsondata['thumbnail_url']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['performers'] = []
        for model in jsondata['porn_star_lead']:
            item['performers'].append(model['name'])
        item['tags'] = jsondata['tag_input']
        item['url'] = 'https://www.fuckpassvr.com/video/' + jsondata['slug']
        item['id'] = jsondata['id']
        if jsondata['duration_display']:
            item['duration'] = self.duration_to_seconds(jsondata['duration_display'])
        item['trailer'] = None
        item['network'] = "FuckPassVR"
        item['site'] = "FuckPassVR"
        item['parent'] = "FuckPassVR"
        item['type'] = 'Scene'

        yield self.check_item(item, self.days)
