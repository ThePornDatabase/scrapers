import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKaterinaHartlovaSpider(BaseSceneScraper):
    name = 'KaterinaHartlova'
    network = 'Katerina Hartlova'
    parent = 'Katerina Hartlova'
    site = 'Katerina Hartlova'

    start_urls = [
        'https://tour.katerina-hartlova.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/scenes?page=%s&order_by=publish_date&sort_by=desc',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = self.init_scene()
                item['site'] = scene['site']
                item['parent'] = scene['site']
                item['network'] = "Katerina Hartlova"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'] = scene['models']
                item['performers_data'] = self.get_performers_data(item['performers'])
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                if "nympho" in response.url:
                    item['id'] = scene['slug']
                else:
                    item['id'] = scene['id']
                if "sidechick" in response.url:
                    item['image'] = scene['trailer_screencap'].replace(" ", "%20")
                else:
                    item['image'] = scene['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['tags'] = scene['tags']
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                item['url'] = f"https://tour.{scene['site_domain']}/scenes/{scene['slug']}"

                yield self.check_item(item, self.days)

    def get_performers_data(self, performer_list):
        performers_data = []
        if len(performer_list):
            for performer in performer_list:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Katerina Hartlova"
                perf['site'] = "Katerina Hartlova"
                performers_data.append(perf)
        return performers_data
