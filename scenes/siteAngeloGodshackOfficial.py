import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAngeloGodshackOfficialSpider(BaseSceneScraper):
    name = 'AngeloGodshackOfficial'
    network = 'Angelo Godshack'
    parent = 'Angelo Godshack Official'
    site = 'Angelo Godshack Official'

    start_urls = [
        'https://angelogodshackxxx.com',
    ]

    selector_map = {
        'title': '//div[@class="video-detail"]//div[contains(@class, "header")]/h1/text()',
        'description': '//div/strong[contains(text(), "Description")]/../following-sibling::p/text()',
        'date': '',
        'image': '//video-js/@data-poster',
        'performers': '//div[contains(@class,"video-detail__description")]//div[@class="title"]/text()',
        'tags': '',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)$',
        'pagination': '/newest?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "library-item")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
