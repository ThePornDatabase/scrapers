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
            item['duration'] = self.duration_to_seconds(jsondata['duration_display'])
            item['trailer'] = jsondata['preview_video_url']
            item['network'] = "FuckPassVR"
            item['site'] = "FuckPassVR"
            item['parent'] = "FuckPassVR"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
