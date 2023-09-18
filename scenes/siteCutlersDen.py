import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCutlersDenSpider(BaseSceneScraper):
    name = 'CutlersDen'
    network = 'Cutlers Den'
    parent = 'Cutlers Den'
    site = 'Cutlers Den'

    start_urls = [
        'https://cutlersden.com',
    ]

    selector_map = {
        'title': '//div[@class="content-details"]/div/h1/text()',
        'description': '//div[@class="content-details"]/p/text()',
        'date': '//div[@class="content-details"]//div[contains(@class,"content-date")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="player-window-play"]/following-sibling::img/@src0_4x|//div[@class="player-window-play"]/following-sibling::img/@src0_3x|//div[@class="player-window-play"]/following-sibling::img/@src0_2x|//div[@class="player-window-play"]/following-sibling::img/@src0_1x',
        'performers': '//div[@class="content-details"]//div[contains(@class,"vCategories")]/a[contains(@href, "models")]/text()',
        'tags': '//div[@class="content-details"]//div[contains(@class,"vCategories")]/a[contains(@href, "categories")]/text()',
        'duration': '//div[@class="content-details"]//div[contains(@class,"content-date")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class')
            if sceneid:
                meta['id'] = re.search(r'(.*?)_', sceneid.get()).group(1)
            else:
                meta['id'] = None
            link = scene.xpath('./a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href')
        for scene in scenes:
            link = scene.get()
            meta['id'] = re.search(r'.*/(.*?)\.htm', link).group(1)
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
