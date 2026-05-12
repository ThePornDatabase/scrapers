import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLustRealitySpider(BaseSceneScraper):
    name = 'LustReality'
    network = 'LustReality'
    parent = 'LustReality'
    site = 'LustReality'

    start_urls = [
        'https://www.lustreality.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "rightWrapper")]//h2/text()',
        'description': '//p[contains(@class, "filmDescription")]/following-sibling::div//text()',
        'date': '//div[contains(@class, "rightWrapper")]//span[contains(@class, "date")]/text()',
        're_date': r'(\d+\w+?\s\w{3,4}\s\d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "rightWrapper")]//span[contains(@class, "infoModelNames")]/a/text()',
        'tags': '//div[contains(@class, "rightWrapper")]//span[contains(@class, "infoTitle")]/following-sibling::a/text()',
        'duration': '//div[contains(@class, "rightWrapper")]//span[contains(@class, "time")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{1,2}\:\d{2})',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videos__element"]/a/@href').getall()
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
                perf['extra']['gender'] = "Female"
                perf['network'] = self.get_network(response)
                perf['site'] = self.get_network(response)
                performers_data.append(perf)
        return performers_data
    
    def get_tags(self, response):
        tags = super().get_tags(response)
        if 'Virtual Reality' not in tags:
            tags.append('Virtual Reality')
        return sorted(filter(None, tags))

