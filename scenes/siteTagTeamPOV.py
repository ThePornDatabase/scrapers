import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTagTeamPOVSpider(BaseSceneScraper):
    name = 'TagTeamPOV'
    network = 'Spizoo'
    parent = 'TagTeamPOV'
    site = 'TagTeamPOV'

    start_urls = [
        'https://www.tagteampov.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/h1/text()',
        'description': '//div[contains(@class, "description")]/p/text()',
        'date': '//h2[contains(text(), "Release")]/following-sibling::p/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//div[@id="block-content"]/img/@src',
        'performers': '//h2[contains(text(), "Pornstars")]/following-sibling::span[1]/a/@title',
        'tags': '//div[contains(@class, "categories-holder")]/a/@title',
        'duration': '//h4[contains(text(), "Length")]/following-sibling::p/text()|//h2[contains(text(), "Length")]/following-sibling::p/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/videos_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "title-label")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        return super().get_id(response).lower()
