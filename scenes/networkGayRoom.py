import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkGayRoomSpider(BaseSceneScraper):
    name = 'GayRoom'
    network = 'GayRoom'

    start_urls = [
        'https://bathhousebait.com',
        'https://boysdestroyed.com',
        'https://damnthatsbig.com',
        'https://gaycastings.com',
        'https://gaycreeps.com',
        'https://gayviolations.com',
        'https://massagebait.com',
        'https://menpov.com',
        'https://officecock.com',
        'https://outhim.com',
        'https://showerbait.com',
        'https://thickandbig.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class,"text-2xl")]/text()',
        'description': '//div[contains(@class,"scene-info")]/div/span/text()',
        'date': '',
        'image': '//video[@id="player"]/@poster|//div[contains(@id, "player")]//img/@src',
        'performers': '//span[contains(text(), "Featuring")]/following-sibling::a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"video-thumbnail-footer")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']

    def get_image(self, response):
        image = super().get_image(response)
        if "?" in image:
            image = re.search(r'(.*)\?', image).group(1)
        return image
