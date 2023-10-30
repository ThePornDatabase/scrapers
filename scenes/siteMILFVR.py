import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMILFVRSpider(BaseSceneScraper):
    name = 'MILFVR'
    network = 'MILFVR'
    parent = 'MILFVR'
    site = 'MILFVR'

    start_urls = [
        'https://www.milfvr.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "header-lg")]/h1[@class="detail__title"]/text()',
        'description': '//script[contains(@type,"ld+json")]/text()',
        're_description': r'description[\'\"].*?[\'\"](.*?)[\'\"],',
        'date': '//script[contains(@type,"ld+json")]/text()',
        're_date': r'uploadDate[\'\"].*?[\'\"](.*?)[\'\"],',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="detail__models" and contains(text(), "Starring")]/a/text()',
        'tags': '//div[contains(@class,"tag-list__body")]//a/text()',
        'duration': '//script[contains(@type,"ld+json")]/text()',
        're_duration': r'duration[\'\"].*?[\'\"](.*?)[\'\"],',
        'trailer': '',
        'external_id': r'.*-(\d+)$',
        'pagination': '/?o=d&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card__body"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
