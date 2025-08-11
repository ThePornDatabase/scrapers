import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJeffsModelsSpider(BaseSceneScraper):
    name = 'JeffsModels'
    network = 'Jeffs Models'
    parent = 'Jeffs Models'
    site = 'Jeffs Models'

    start_urls = [
        'https://jeffsmodels.com',
    ]

    selector_map = {
        'title': '//div[@class="section-title"]/h4/text()|//div[@class="section-title"]/h1/text()',
        'description': '//div[@class="section-content"]//p[contains(@class, "read")]/text()',
        'date': '//div[@class="section-content"]//small[contains(@class,"updated")]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[contains(@class,"model-player")]//video/@poster|//div[contains(@class,"model-player")]/a/img/@src',
        'performers': '//div[@class="section-content"]//h4/a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="section-content"]//div[contains(@class, "categories")]/a/text()',
        'duration': '',
        'trailer': '//div[contains(@class,"model-player")]//video/source/@src',
        'external_id': r'update/(\d+)/',
        'pagination': '/updates/?page=%s&step=2',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-wrapper"]/a/@href').getall()
        for scene in scenes:
            if "?nats=" in scene:
                scene = re.search(r'(.*)\?nats=', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Bbw" not in tags:
            tags.append("BBW")
        return tags
