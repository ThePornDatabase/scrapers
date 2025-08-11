import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLinaMilaSpider(BaseSceneScraper):
    name = 'LinaMila'
    network = 'LinaMila'
    parent = 'LinaMila'
    site = 'LinaMila'

    start_urls = [
        'https://www.linamila.tv',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[@class="inner"]/div[contains(@class, "custom_text")]/p/text()',
        'date': '//i[contains(@class, "calendar")]/following-sibling::span[1]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '',
        'duration': '//div[@class="view-card" and contains(text(), "minutes")]/span/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/collections/page/%s?media=video',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Lina Mila']
