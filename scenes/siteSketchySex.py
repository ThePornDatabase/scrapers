import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSketchySexSpider(BaseSceneScraper):
    name = 'SketchySex'
    network = 'Sketchy Sex'
    parent = 'Sketchy Sex'
    site = 'Sketchy Sex'

    start_urls = [
        'https://www.sketchysex.com',
    ]

    selector_map = {
        'title': '//div[@class="info"]/div[@class="name"]/span/text()',
        'description': '//div[@class="VideoDescription"]/text()',
        'date': '//div[@class="info"]/div[@class="date"]/text()',
        're_date': r'(\w+ \d+, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//script[contains(text(), "poster")]/text()',
        're_image': r'poster.*?(http.*?)[\'\"]',
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
        scenes = response.xpath('//div[@class="episode-item"]//a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']
