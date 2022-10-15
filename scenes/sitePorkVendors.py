import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePorkVendorsSpider(BaseSceneScraper):
    name = 'PorkVendors'
    network = 'Pork Vendors'
    parent = 'Pork Vendors'
    site = 'Pork Vendors'

    start_urls = [
        'https://porkvendors.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class,"title_bar")]/text()',
        'description': '//p[@class="description-text"]/text()',
        'date': '//label[contains(text(), "Date")]/following-sibling::p[1]/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//video/@poster',
        'performers': '//div[contains(@class,"videobg")]//span[@class="update_models"]/a/text()',
        'tags': '//a[contains(@href, "/categories/")]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="updateimg"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
