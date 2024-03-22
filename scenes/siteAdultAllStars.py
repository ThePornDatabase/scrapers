import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAdultAllStarsSpider(BaseSceneScraper):
    name = 'AdultAllStars'
    network = 'Adult All Stars'
    parent = 'Adult All Stars'
    site = 'Adult All Stars'

    start_urls = [
        'https://www.adultallstars.com',
    ]

    selector_map = {
        'title': '//div[@class="update_table_left"]//span[contains(@class, "update_title")]/text()',
        'description': '//div[@class="update_table_left"]//span[contains(@class, "latest_update")]/text()',
        'date': '//div[@class="update_table_left"]//span[contains(@class, "availdate")]/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//div[@class="update_table_right"]/div[contains(@class, "update_image")]/a/img[1]/@src',
        'performers': '//div[@class="update_table_left"]//span[contains(@class, "update_models")]/a/text()',
        'tags': '//div[@class="update_table_left"]//span[contains(@class, "update_tags")]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
