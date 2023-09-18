import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteYoungBastardsSpider(BaseSceneScraper):
    name = 'YoungBastards'
    network = 'Young Bastards'
    parent = 'Young Bastards'
    site = 'Young Bastards'

    start_urls = [
        'https://youngbastards.com',
    ]

    selector_map = {
        'title': '//div[@class="videonewinfo"]/h2/text()',
        'description': '//div[@class="videonewinfo"]/p[1]/text()',
        'date': '//div[@class="videonewinfo"]/h5/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "sources")]/text()',
        're_image': r'image:.*?[\'\"](.*?)[\'\"]',
        'performers': '//div[@class="videonewinfo"]/p[2]/text()',
        'tags': '',
        'duration': '//div[@class="videonewinfo"]/h5/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/?videos/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="itemv"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="videonewinfo"]/p[2]/text()')
        if performers:
            performers = performers.get()
            performers = performers.replace("Cast:", "").strip()
            if performers:
                performers = performers.split(",")
                return list(map(lambda x: x.strip().title(), performers))
        return []

    def get_tags(self, response):
        return ['Gay']
