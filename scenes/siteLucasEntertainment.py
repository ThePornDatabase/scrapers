import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLucasEntertainmentSpider(BaseSceneScraper):
    name = 'LucasEntertainment'
    network = 'Lucas Entertainment'
    parent = 'Lucas Entertainment'
    site = 'Lucas Entertainment'

    start_urls = [
        'https://www.lucasentertainment.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//p[@class="p1"]/text()',
        'date': '//p[@class="plain-link"]/strong[contains(text(), "Date")]/following-sibling::text()',
        'date_formats': ['%B %d %Y'],
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//p[@class="plain-link"]/strong[contains(text(), "From")]/following-sibling::a[contains(@href, "/models/")]/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/scenes/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "scene-item")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
