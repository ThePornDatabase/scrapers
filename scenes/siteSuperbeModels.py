import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSuperbeModelsSpider(BaseSceneScraper):
    name = 'SuperbeModels'
    network = 'Superbe Models'
    parent = 'Superbe Models'
    site = 'Superbe Models'

    start_urls = [
        'https://www.superbemodels.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@itemprop="description"]/@content',
        'date': '//div[contains(@class, "h5-published")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@itemprop="thumbnailUrl"]/@content|//picture[@class="-vcc-picture"]//img/@src',
        'performers': '//h2/span/a//text()',
        'tags': '//div[contains(@class, "h5")]//a[contains(@href, "categories")]/text()',
        'external_id': r'watch/(\d+)/',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/films.en.html?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="-g-vc-superbe"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
