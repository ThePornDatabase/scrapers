import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRealJamVRSpider(BaseSceneScraper):
    name = 'RealJamVR'
    network = 'realjamvr'
    parent = 'realjamvr'
    site = 'realjamvr'

    start_urls = [
        'https://realjamvr.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "header-title")]/text()',
        'description': '//div[contains(@class, "item-desc")]//text()',
        'date': '//div[contains(@class, "item-header-date")]/span/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "item-header-featuring")]/a/text()',
        'tags': '//div[contains(@class, "video-item-tags")]/a/text()',
        'trailer': '',
        'external_id': r'/id/(.*)',
        'pagination': '/virtualreality/list/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"list-item")]/a[contains(@class, "list-link")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
