import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class TonightsGirlfriendSpider(BaseSceneScraper):
    name = 'TonightsGirlfriend'
    network = 'Tonights Girlfriend'
    parent = 'Tonights Girlfriend'

    start_urls = [
        'https://www.tonightsgirlfriend.com'
    ]

    selector_map = {
        'description': ".scenepage-description::text",
        'performers': "//div[@class='scenepage-info']/p/a/text()",
        'date': "//span[@class='scenepage-date']/text()",
        'image': "//img[@class='playcard']/@src",
        'tags': '',
        'external_id': r'scene/(.+)',
        'trailer': '',
        'pagination': r'/scenes?page=%s'
    }

    def get_title(self, response):
        externid = self.get_id(response).replace('-', ' ')
        externid = re.sub(r"(\d+)$", "", externid)
        return externid.title()

    def get_scenes(self, response):
        scenes = response.css(
            'div.panel .scene-thumbnail a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
