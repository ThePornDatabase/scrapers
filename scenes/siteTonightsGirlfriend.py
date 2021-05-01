import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class TonightsGirlfriendSpider(BaseSceneScraper):
    name = 'TonightsGirlfriend'
    network = 'Tonights Girlfriend'

    start_urls = [
        'https://www.tonightsgirlfriend.com'
    ]

    selector_map = {
        'description': ".scenepage-description::text",
        'performers': "//div[@class='scenepage-info']/p/a/text()",
        'date': "//span[@class='scenepage-date']/text()",
        'image': "//img[@class='playcard']/@src",
        'tags': '',
        'external_id': 'scene/(.+)',
        'trailer': '',
        'pagination': '/scenes?page=%s'
    }

    def get_date(self, response):
        data = response.xpath(self.selector_map['date']).get().replace('Added:', '').strip()
        return dateparser.parse(data).isoformat()

    def get_title(self, response):
        id = self.get_id(response).replace('-', ' ')
        id = re.sub("(\d+)$", "", id)
        return id.title()

    def get_scenes(self, response):
        scenes = response.css('div.panel .scene-thumbnail a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
