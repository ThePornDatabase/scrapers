import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteInkaPornSpider(BaseSceneScraper):
    name = 'InkaPorn'
    network = 'InkaPorn'

    start_urls = [
        'https://www.inkaporn.com',
        'https://www.inkasex.com',
        'https://www.xekeko.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//p[contains(@itemprop, "description")]/text()',
        'date': '//script[contains(text(), "uploadDate")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/videos/latest?page_id=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video-title"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        return super().get_id(response).lower()
