import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMom4kSpider(BaseSceneScraper):
    name = 'Mom4k'
    network = 'Mom4k'
    parent = 'Mom4k'
    site = 'Mom4k'

    start_urls = [
        'https://mom4k.com',
    ]

    selector_map = {
        'title': '//div[contains(@id, "side")]/h1/text()',
        'description': '//div[contains(@id, "description")]/text()',
        'date': '//div[contains(text(), "RELEASED")]/span/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//video/@poster',
        'performers': '//div[contains(@id, "models")]/a/text()',
        'tags': '',
        'external_id': r'.*/(.*?)$',
        'trailer': '',
        'pagination': '/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="btn-group"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        return ['Interracial']
