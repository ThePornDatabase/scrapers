import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFuckerMateSpider(BaseSceneScraper):
    name = 'FuckerMate'
    network = 'Fucker Mate'
    parent = 'Fucker Mate'
    site = 'Fucker Mate'

    start_urls = [
        'https://www.fuckermate.com',
    ]

    selector_map = {
        'title': '//section[@id="video-section"]//div[contains(@class, "post-header")]/h1[1]/text()',
        'description': '//section[@id="video-section"]//div[contains(@class, "post-entry")]/div/div/p[1]/text()',
        'date': '//section[@id="video-section"]//div[contains(@class, "post-meta")]/text()[1]',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//section[@id="video-section"]//div[@id="video-frame"]/videoplayer/@poster',
        'performers': '//div[@class="team-item"]/following-sibling::div[1]//h1/a/text()',
        'tags': '//section[@id="video-section"]//div[contains(@class, "post-meta")]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'video/(.*)',
        'pagination': '/video?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "post-thumbnail")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
