import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteComeInsideSpider(BaseSceneScraper):
    name = 'ComeInside'
    network = 'Come Inside'

    start_urls = [
        'https://comeinside.com',
    ]

    selector_map = {
        'external_id': r'scenes/(\d+?)/',
        'pagination': '/scenes?page=%s'
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
            jsondata = jsondata['props']['pageProps']
            item = SceneItem()
            item['site'] = "Come Inside"
            item['parent'] = "Come Inside"
            item['network'] = "Come Inside"
            item['title'] = self.cleanup_title(jsondata['playlist']['name'])
            item['description'] = self.cleanup_text(jsondata['playlist']['description'])
            item['performers'] = jsondata['playlist']['models']
            item['date'] = self.parse_date(jsondata['playlist']['publish_date']).isoformat()
            item['id'] = jsondata['playlist']['id']
            item['image'] = jsondata['playlist']['thumb']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = jsondata['content']['tags']
            item['trailer'] = jsondata['content']['trailer_url']
            item['url'] = f"https://comeinside.com/scenes/{item['id']}/{jsondata['playlist']['slug']}"

            yield self.check_item(item, self.days)
