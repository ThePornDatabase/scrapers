import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMaxHardcoreSpider(BaseSceneScraper):
    name = 'MaxHardcore'
    site = 'Max Hardcore'
    parent = 'Max Hardcore'
    network = 'Max Hardcore'

    start_urls = [
        'https://www.max-hardcore.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "mhead")]/text()',
        'description': '//div[@class="description__inner"]/text()',
        'date': '//span[@class="mstats-list__label" and re:test(text(), "\d{4}-\d{2}-\d{2}")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h4[contains(text(), "odels")]/../../following-sibling::div/ul/li/a//text()',
        'tags': '//ul[@class="tag-list"]/li/a[contains(@href, "channels")]/text()',
        'duration': '//span[contains(@class, "mstats-list")]/span[contains(@class,"icon") and contains(@class, "time")]/../following-sibling::span[1]/text()',
        'trailer': '',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/most-recent/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item__inner" and not(contains(./a[1]/@href, "preview"))]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
