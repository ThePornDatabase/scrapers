import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXXCelSpider(BaseSceneScraper):
    name = 'XX-Cel'
    network = 'XX-Cel'
    parent = 'XX-Cel'
    site = 'XX-Cel'

    start_urls = [
        'https://xx-cel.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "vid-details")]//h2/text()',
        'description': '',
        'date': '//div[contains(@class, "vid-details")]//span[contains(text(), "eleased")]/strong/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@id="videoPlayer"]//video/@poster|//div[@id="videoPlayer"]/a/img/@src',
        'performers': '//div[contains(@class, "vid-details")]//span[contains(text(), "tarring")]/a/text()',
        'tags': '',
        'duration': '//div[contains(@class, "vid-details")]//span[contains(text(), "uration")]/strong/text()',
        'trailer': '//div[@id="videoPlayer"]//video/source/@src',
        'external_id': r'.*/(.*?)$',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "star col-xxl-3")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
