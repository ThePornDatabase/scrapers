import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDanniSpider(BaseSceneScraper):
    name = 'Danni'
    network = 'Sexual Prime'
    parent = 'Danni'
    site = 'Danni'

    start_urls = [
        'https://www.danni.com',
    ]

    selector_map = {
        'title': '//div[@class="scene-title"]/text()',
        'description': '',
        'date': '',
        'image': '//script[contains(text(), "vJSPlayer")]/text()',
        're_image': r'poster.*?(http.*?)[\'\"]',
        'performers': '//div[@class="scene-title"]/following-sibling::div[contains(@class, "model-list")]/a/text()',
        'tags': '//div[@class="scene-title"]/following-sibling::div[contains(@class, "scene-tags")]/a/text()',
        'duration': '//div[contains(@class, "danni-clock")]/following-sibling::span/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)_vid',
        'pagination': '/categories/videos_%s_d',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="danni-card-name-wrapper"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        return super().get_id(response).lower()
