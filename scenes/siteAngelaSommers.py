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
        'title': '//div[@class="pagetitle"]/div/h1/text()',
        'description': '//div[@class="videocontent"]/p/text()',
        'date': '//p[@class="date"]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="videoplayer"]/img/@src0_3x',
        'performers': '//p[@class="modelname"]/span/a/text()',
        'tags': '',
        'external_id': r'trailers/(.*?).html',
        'trailer': '',
        'pagination': '/tour1/categories/Movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "modelfeature")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
