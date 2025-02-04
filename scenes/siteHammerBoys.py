import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHammerBoysSpider(BaseSceneScraper):
    name = 'HammerBoys'
    site = 'HammerBoys'
    parent = 'HammerBoys'
    network = 'HammerBoys'

    start_urls = [
        'https://hammerboys.tv'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"update_description")]/text()',
        'date': '//span[contains(@class,"availdate")]/text()',
        'date_formats': ['%d.%m.%Y'],
        'image': '//div[@class="update_image"]/comment()[contains(., "First")]/following-sibling::a[1]/img/@src0_2x',
        'performers': '//span[contains(@class,"update_models")]/a/text()',
        'tags': '',
        'trailer': '//div[@class="update_image"]/a[contains(@onclick, "trailers")][1]/@onclick',
        're_trailer': r'(/trailer.*?)[\'\"]',
        'type': 'Scene',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/Movies_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        return image.replace("-2x", "-full")

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_tags(self, response):
        return ['Gay']

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "HammerBoys"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
