import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteShyGirlsSpider(BaseSceneScraper):
    name = 'ShyGirls'
    site = 'ShyGirls'
    parent = 'ShyGirls'
    network = 'ShyGirls'

    start_urls = [
        'https://shy-girls.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "short-description")]/p[1]/text()',
        'image': '//img[contains(@class, "iconic-woothumbs-images")]/@data-srcset',
        're_image': r'(http.*?) .*',
        'performers': '',
        'tags': '//span[@class="tagged_as"]/a/text()',
        'duration': '//div[contains(@class, "short-description")]//text()[contains(., "Runtime")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/scenes/?product-page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class,"sales-flash-overlay")]/a[contains(@href, "product")]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = response.xpath('//article/@id').get()
        return re.search(r'(\d+)', sceneid).group(1)

    def get_image(self, response):
        image = super().get_image(response)
        if "wp-content" not in image:
            image = ""
        return image
