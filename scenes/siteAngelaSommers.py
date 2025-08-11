import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAngelaSommersSpider(BaseSceneScraper):
    name = 'AngelaSommers'
    network = 'Angela Sommers'
    parent = 'Angela Sommers'
    site = 'Angela Sommers'

    start_urls = [
        'https://angelasommers.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//div[@class="update_block_info"]//text()[contains(., "/")]',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "tour_update_models")]/a/text()',
        'tags': '//span[contains(@class, "update_tags")]/a/text()',
        'external_id': r'updates/(.*?).html',
        'trailer': '',
        'pagination': '/categories/Movies_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "updateItem")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
