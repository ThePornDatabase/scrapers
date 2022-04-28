import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SieTeenyTabooSpider(BaseSceneScraper):
    name = 'TeenyTaboo'
    network = 'Teeny Taboo'
    parent = 'Teeny Taboo'
    site = 'Teeny Taboo'

    start_urls = [
        'https://www.teenytaboo.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "customhcolor")]/text()',
        'description': '//h2[contains(@class, "customhcolor")]/text()',
        'date': '//span[@class="date"]/text()',
        'date_formats': ['%B %d %Y'],
        'image': '//center/img/@src',
        'image_blob': True,
        'performers': '//h3[contains(@class, "customhcolor")]/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'videos/(\d+)/',
        'pagination': '/videos/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"videoimg_wrapper")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        return string.capwords(title.replace("-", " "))

    def get_tags(self, response):
        tags = response.xpath('//h4[contains(@class, "customhcolor")]/text()')
        if tags:
            tags = tags.get().split(",")
            return list(map(lambda x: string.capwords(x.strip()), tags))
        return []
