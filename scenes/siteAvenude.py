import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAvenudeSpider(BaseSceneScraper):
    name = 'Avenude'
    network = 'Avenude'
    parent = 'Avenude'
    site = 'Avenude'

    start_urls = [
        'https://avenude.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//p[@class="card-text"]/following-sibling::p//text()',
        'image': '//div[@class="container"]//div[contains(@class, "card") and contains(@class, "mt-4")]/a/img/@src',
        'performers': '//div[@class="container"]//a[contains(@href, "/model/")]/text()',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?&page_videos=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="card-body"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
