import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOldje3someSpider(BaseSceneScraper):
    name = 'Oldje3some'
    network = 'Oldje'
    parent = 'Oldje'
    site = 'Oldje 3some'

    start_urls = [
        'https://www.oldje-3some.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "updates")]/div/div/h1/text()',
        'description': '//div[contains(@class, "description")]//p/text()',
        'image': '//div[contains(@class, "teaser-img")]/a/img/@src',
        'performers': '//div[contains(@class, "updates")]//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="tags"]/a//text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/page/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "read-more")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
