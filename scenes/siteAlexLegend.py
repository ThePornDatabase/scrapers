import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAlexLegendSpider(BaseSceneScraper):
    name = 'AlexLegend'
    network = 'AlexLegend'
    parent = 'AlexLegend'
    site = 'AlexLegend'

    start_urls = [
        'https://alexlegend.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "content-title")]/h1/text()',
        'description': '',
        'date': '//div[@class="content-date"]/div[contains(@class, "label")]/text()',
        'date_formats': ['%d.%m.%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//aside//div[contains(@class, "main__models")]//a//text()',
        'tags': '//aside//div[contains(@class, "content-tags")]//a//text()',
        'duration': '//div[@class="content-time"]/div[contains(@class, "label")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//video/source/@src',
        'external_id': r'.*-(\d+)',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-col")]/div[1]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[@class="item-date"]/span/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%d.%m.%Y']).strftime('%Y-%m-%d')
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
