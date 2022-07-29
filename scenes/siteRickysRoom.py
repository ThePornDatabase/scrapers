import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteRickysRoomSpider(BaseSceneScraper):
    name = 'RickysRoom'
    network = 'Rickys Room'

    start_urls = [
        'https://rickysroom.com',
    ]

    selector_map = {
        'external_id': r'videos/.*',
        'pagination': '/videos?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="video-info"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']
            item = SceneItem()
            item['site'] = "Rickys Room"
            item['parent'] = "Rickys Room"
            item['network'] = "Rickys Room"
            item['title'] = self.cleanup_title(jsondata['content']['title'])
            item['description'] = self.cleanup_text(jsondata['content']['description'])
            item['performers'] = jsondata['content']['models']
            item['date'] = self.parse_date(jsondata['content']['publish_date']).isoformat()
            item['id'] = jsondata['content']['id']
            item['image'] = jsondata['content']['thumb'].replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = jsondata['content']['tags']
            item['trailer'] = jsondata['content']['trailer_url'].replace(" ", "%20")
            item['url'] = f"https://rickysroom.com/videos/{jsondata['content']['slug']}"

            yield self.check_item(item, self.days)
