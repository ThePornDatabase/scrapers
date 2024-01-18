import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteRandyBlueSpider(BaseSceneScraper):
    name = 'RandyBlue'
    network = 'RandyBlue'
    parent = 'RandyBlue'
    site = 'RandyBlue'

    start_urls = [
        'https://www.randyblue.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "title-zone")]//h1/text()',
        'description': '//div[@class="panel-body"]/text()',
        'date': '//div[contains(@class, "title-zone")]//span[contains(@class, "calendar")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@id="trailer_player_finished"]//img[contains(@src, "/content/")]/@src',
        'performers': '//div[contains(@class, "title-zone")]//ul[@class="scene-models-list"]/li/a/text()',
        'tags': '//div[contains(@class, "title-zone")]//ul[@class="scene-tags"]/li/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'scenes/(.*)\.htm',
        'pagination': '/categories/videos_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class, "scene-video")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
