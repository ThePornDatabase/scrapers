import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGuysInSweatpantsSpider(BaseSceneScraper):
    name = 'GuysInSweatpants'
    network = 'Guys In Sweatpants'
    parent = 'Guys In Sweatpants'
    site = 'Guys In Sweatpants'

    cookies = {"pp-accepted": "true"}

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//h1[@class="title"]/following-sibling::div[@class="meta"]/following-sibling::p[1]/text()',
        'date': '//h1[@class="title"]/following-sibling::div[@class="meta"]/span/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//img[@class="bkg"]/@src',
        'performers': '//h1[@class="title"]/following-sibling::div[@class="meta"]/span/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request("https://guysinsweatpants.com/scenes", callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[@class="gallery-item-1"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
