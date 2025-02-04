import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSuzieQHasBigBoobsSpider(BaseSceneScraper):
    name = 'SuzieQHasBigBoobs'
    network = 'Suzie Q Has Big Boobs'
    parent = 'Suzie Q Has Big Boobs'
    site = 'Suzie Q Has Big Boobs'

    start_urls = [
        'https://www.suzieqhasbigboobs.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "title")]/h2/text()',
        'description': '//div[contains(@class, "modelContent")]/p/text()',
        'date': '//div[contains(@class, "featuring") and contains(text(), "Release date")]/text()',
        're_date': r'(\d{1,2} \w+, \d{4})',
        'image': '//meta[@property="og:image"]/@content|//meta[@property="twitter:image"]/@content',
        'performers': '//div[contains(@class, "featuring")]/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=[\'\"](.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour2/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoPic")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
