import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTSPlaygroundSpider(BaseSceneScraper):
    name = 'TSPlayground'
    network = 'TSPlayground'
    parent = 'TSPlayground'
    site = 'TSPlayground'

    start_urls = [
        'https://tsplayground.com',
    ]

    selector_map = {
        'title': '//div[@class="content-title"]/h1/text()',
        'description': '//div[contains(@class, "more-desc")]/h2/..//text()',
        'date': '//div[@class="content-date"]/div/text()',
        're_date': r'(\d{1,2}\.\d{1,2}\.\d{4})',
        'date_formats': ['%d.%m.%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="content-models"]/a/span/text()',
        'tags': '//div[@class="content-tags"]/a/text()',
        'duration': '//div[@class="content-time"]/div/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//video/source[1]/@src',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-col") and contains(@class, "-video")]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Transgender Female"
                perf['network'] = "TSPlayground"
                perf['site'] = "TSPlayground"
                performers_data.append(perf)
        return performers_data
