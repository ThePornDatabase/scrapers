import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteIsiahMaxwellSpider(BaseSceneScraper):
    name = 'IsiahMaxwell'
    network = 'Isiah Maxwell'
    parent = 'Isiah Maxwell'
    site = 'Isiah Maxwell'

    start_urls = [
        'https://tour.isiahmaxwellxxx.com',
    ]

    selector_map = {
        'title': '//span[@class="medium-blue"]/text()',
        'description': '',
        'date': '',
        'image': '//div[@id="endscreen"]/@style',
        're_image': r'(http.*\.jpg)',
        'performers': '//p[@class="featuring"]/a/text()',
        'tags': '//p[@class="category"]/a/text()',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*)\.htm',
        'pagination': '/?&spage=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
