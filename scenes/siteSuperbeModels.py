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
        'date': '//div[@class="-mvd-grid-stats"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@itemprop="thumbnailUrl"]/@content|//picture[@class="-vcc-picture"]//img/@src',
        'performers': '//div[contains(@class, "-mvd-grid-actors")]/span/a/text()',
        'tags': '//div[@class="-mvd-list"]/span/a/text()',
        'duration': '//meta[@itemprop="duration"]/@content',
        'external_id': r'watch/(\d+)/',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/films.en.html?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "global-multi-card")]//a[contains(@href, "/watch/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
