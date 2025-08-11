import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLuxePlayhouseSpider(BaseSceneScraper):
    name = 'LuxePlayhouse'
    network = 'LuxePlayhouse'
    parent = 'LuxePlayhouse'
    site = 'LuxePlayhouse'

    start_urls = [
        'https://luxeplayhouse.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "update-info")]/h1/text()',
        'description': '',
        'date': '//span[contains(text(), "ADDED")]/following-sibling::span[1]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "poster")]/text()',
        're_image': r'poster=[\'\"](http.*?)[\'\"]',
        'performers': '//ul[contains(@class, "luxe-list")]/li/a[contains(@href, "/models/")]/text()',
        'tags': '//ul[contains(@class, "luxe-list")]/li/a[contains(@href, "/categories/")]/text()',
        'duration': '//span[contains(text(), "RUNTIME")]/following-sibling::span[1]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//span[contains(@class, "item-title")]/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
