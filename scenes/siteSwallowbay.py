import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSwallowbaySpider(BaseSceneScraper):
    name = 'Swallowbay'
    network = 'Swallowbay'
    parent = 'Swallowbay'
    site = 'Swallowbay'

    start_urls = [
        'https://swallowbay.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="content-desc more-desc"]//text()',
        'date': '//div[@class="content-date"]',
        're_date': r'(\d{1,2}\w{1,2}? \w+ \d{4})',
        'date_formats': ['%d %b %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="content-models"]/a//text()',
        'tags': '//div[@class="content-tags"]//a/text()',
        'trailer': '//dl8-video/source[1]/@src',
        'external_id': r'video/(.*)\.html',
        'pagination': '/videos/page%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-name"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
