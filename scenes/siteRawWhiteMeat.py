import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRawWhiteMeatSpider(BaseSceneScraper):
    name = 'RawWhiteMeat'
    network = 'Raw White Meat'
    parent = 'Raw White Meat'
    site = 'Raw White Meat'

    start_urls = [
        'https://rawwhitemeat.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="post-entry"]/p/text()',
        'date': '',
        'image': '//div[@class="player_responsive"]//video/@poster',
        'performers': '//a[contains(@href, "video_tag")]/text()',
        'tags': '',
        'trailer': '//div[@class="player_responsive"]//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-img"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
