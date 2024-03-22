import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMatureFetishSpider(BaseSceneScraper):
    name = 'MatureFetish'
    network = 'Mature NL'
    parent = 'Mature Fetish'
    site = 'Mature Fetish'

    start_urls = [
        'https://maturefetish.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h3[contains(text(), "Synopsis")]/following-sibling::text()',
        'date': '//h1/following-sibling::div[1]/div[@class="stats-list"]/div[2]/text()',
        'date_formats': ['%d-%m-%Y'],
        'image': '//video/@poster',
        'performers': '//div[@class="grid-tile-model"]//a[contains(@href, "/model/")]/text()',
        'tags': '//div[contains(@class, "tag-list")]/a/text()',
        'duration': '//div[contains(@style, "max-width")]/following-sibling::div[contains(@class, "stats-list")]/div[1]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/en/content/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid-tile-content"]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
