import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLilMissySpider(BaseSceneScraper):
    name = 'LilMissy'
    network = 'LilMissy'
    parent = 'LilMissy'
    site = 'LilMissy'

    start_urls = [
        'https://lilmissy.uk',
    ]

    selector_map = {
        'title': '//div[contains(@class, "contentD")]/h1/text()',
        'description': '//div[contains(@class, "contentD")]//div[contains(@class, "Description")]/p/text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="models"]/ul/li/a/text()',
        'tags': '//div[@class="tags"]/ul/li/a/text()',
        'duration': '//div[contains(@class, "contentD")]//i[contains(@class, "clock")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoPic")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
