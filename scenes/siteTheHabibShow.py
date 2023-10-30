import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheHabibShowSpider(BaseSceneScraper):
    name = 'TheHabibShow'
    network = 'The Habib Show'
    parent = 'The Habib Show'
    site = 'The Habib Show'

    start_urls = [
        'https://thehabibshow.com',
    ]

    selector_map = {
        'title': '//header/h1/text()',
        'description': '//article[@class="article"]/p//text()',
        'date': '',
        'image': '//div[@class="player"]/@data-poster',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '//div[@class="player"]/@data-video-hd',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/tour/browse/most-recent/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"padding half")]/a[contains(@class,"font-color-orange")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
