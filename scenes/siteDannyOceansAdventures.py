import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Spider(BaseSceneScraper):
    name = 'DannyOceansAdventures'
    network = 'Danny Oceans Adventures'
    parent = 'Danny Oceans Adventures'
    site = 'Danny Oceans Adventures'

    start_urls = [
        'https://dannyoceansadventures.com',
    ]

    selector_map = {
        'title': '//h2[@itemprop="headline"]/text()',
        'description': '//span[@itemprop="about"]//text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '//span[@itemprop="actors"]/a/text()',
        'tags': '//span[@itemprop="keywords"]/a/text()',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/scenes/page/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
