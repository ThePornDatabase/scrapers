import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRLatinaSpider(BaseSceneScraper):
    name = 'VRLatina'
    network = 'VRLatina'
    parent = 'VRLatina'
    site = 'VRLatina'

    start_urls = [
        'https://vrlatina.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "content-title")]/h2/text()',
        'description': '//div[@class="content-desc"]/div[1]/p/text()',
        'date': '//div[contains(text(), "Release date")]/following-sibling::span[1]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(text(), "Starring:")]/following-sibling::a//text()',
        'tags': '//div[contains(text(), "Tags:")]/following-sibling::a//text()',
        'duration': '//div[contains(@class, "length")]/span[contains(text(), ":")]/text()',
        'trailer': '',
        'external_id': r'(\d+)\.htm',
        'pagination': '/most-recent/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-col")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        performers = super().get_performers(response)
        tags2 = []
        for tag in tags:
            if tag not in performers:
                tags2.append(tag)
        return tags2

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "VRLatina"
                perf['site'] = "VRLatina"
                performers_data.append(perf)
        return performers_data
