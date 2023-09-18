import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAltEroticSpider(BaseSceneScraper):
    name = 'AltErotic'
    network = 'Alt Erotic'
    parent = 'Alt Erotic'
    site = 'Alt Erotic'

    start_urls = [
        'https://alterotic.com',
    ]

    cookies = {'close-warning': '1'}

    selector_map = {
        'external_id': r'updates/(.*?)\.html',
        'pagination': '/_next/data/56lUITLyKsV3iowSLtu3y/videos.json?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        if jsondata:
            jsondata = jsondata['pageProps']['contents']
            for scene in jsondata['data']:
                item = SceneItem()
                item['site'] = "Alt Erotic"
                item['parent'] = "Alt Erotic"
                item['network'] = "Alt Erotic"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'] = []
                if "models_slugs" in scene:
                    for performer in scene['models_slugs']:
                        item['performers'].append(performer['name'])
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                item['id'] = scene['id']
                if scene['videos_duration']:
                    item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['image'] = scene['thumb'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['tags'] = scene['tags']
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                item['url'] = f"https://alterotic.com/videos/{scene['slug']}"

                yield self.check_item(item, self.days)
