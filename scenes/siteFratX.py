import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFratXSpider(BaseSceneScraper):
    name = 'FratX'
    network = 'FratX'
    parent = 'FratX'
    site = 'FratX'

    start_urls = [
        'https://fratx.com',
    ]

    selector_map = {
        'title': '//div[@class="name"]/span/text()',
        'description': '//div[@class="VideoDescription"]/text()',
        're_description': r'.*?, \d{4} - (.*)',
        'date': '//div[@class="VideoDescription"]/text()',
        're_date': r'(\w+ \d{1,2}\w{2}?, \d{4})',
        'image': '//div[@class="video-gallery"]/a/img[1]/@src',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'id=(\d+)',
        'pagination': '/index.php?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//comment()[contains(., "start")]/following-sibling::div/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay', 'College']
