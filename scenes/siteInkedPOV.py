import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteInkedPOVSpider(BaseSceneScraper):
    name = 'InkedPOV'
    network = 'Inked POV'

    start_urls = [
        'https://inkedpov.com',
    ]

    selector_map = {
        'external_id': r'scenes/(.*)',
        'pagination': '/scenes?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h4[@class="content-title-wrap"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['content']
            item = SceneItem()
            item['site'] = "Inked POV"
            item['parent'] = "Inked POV"
            item['network'] = "Inked POV"
            item['title'] = self.cleanup_title(jsondata['title'])
            item['description'] = self.cleanup_text(jsondata['description'])
            item['performers'] = jsondata['models']
            item['date'] = self.parse_date(jsondata['publish_date']).isoformat()
            item['id'] = jsondata['id']
            item['image'] = jsondata['thumb']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = jsondata['tags']
            item['trailer'] = jsondata['trailer_url']
            item['url'] = f"https://inkedpov.com/scenes/{jsondata['slug']}"
            item['duration'] = self.duration_to_seconds(jsondata['videos_duration'])
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
