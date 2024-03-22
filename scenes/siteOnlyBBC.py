import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOnlyBBCSpider(BaseSceneScraper):
    name = 'OnlyBBC'
    site = 'Only BBC'
    parent = 'Only BBC'
    network = 'Only BBC'

    start_urls = [
        'https://www.onlybbc.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block_info"]/span[contains(@class, "update_title")]/text()',
        'description': '//div[@class="update_block_info"]/span[contains(@class, "update_description")]/text()',
        'date': '//div[@class="update_block_info"]/span[contains(@class, "availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content|//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="update_block_info"]/span[contains(@class, "update_models")]/a/text()',
        'tags': '//div[@class="update_block_info"]/span[contains(@class, "update_tags")]/a/text()',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
