import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSanktorSpider(BaseSceneScraper):
    name = 'Sanktor'
    network = 'Sanktor'
    parent = 'Sanktor'
    site = 'Sanktor'

    start_urls = [
        'https://sanktor.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "full__desc")]/p[1]//text()',
        'date': '//div[contains(@class, "calendar")]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="video-full"]//span[contains(@class, "flex-video")]//video/@poster',
        'performers': '//div[contains(@class, "full__models")]/a/text()',
        'tags': '',
        'duration': '//div[contains(@class, "clock")]/text()',
        'trailer': '',
        'external_id': r'video/(\d+)/',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video__item"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            perf = {}
            perf['name'] = performer
            perf['site'] = "Sanktor"
            perf['network'] = "Sanktor"
            perf['extra'] = {}
            perf['extra']['gender'] = "Female"
            performers_data.append(perf)
        return performers_data
