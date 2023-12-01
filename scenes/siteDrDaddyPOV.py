import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDrDaddyPOVSpider(BaseSceneScraper):
    name = 'DrDaddyPOV'
    network = 'DrDaddyPOV'
    parent = 'DrDaddyPOV'
    site = 'DrDaddyPOV'

    start_urls = [
        'https://drdaddypov.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/h1/text()',
        'description': '//p[@class="description"]/text()',
        'date': '//h2[contains(text(), "Release Date")]/following-sibling::p/text()',
        'image': '//div[@id="hpromo"]//video/@poster',
        'performers': '//span[@class="update_models"]/a/text()',
        'tags': '//div[@class="categories-holder"]/a/text()',
        'duration': '//h2[contains(text(), "Length")]/following-sibling::p/text()',
        'trailer': '',
        'external_id': r'updates/(.*)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="thumb-pic"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        id = super().get_id(response)
        return id.lower()
