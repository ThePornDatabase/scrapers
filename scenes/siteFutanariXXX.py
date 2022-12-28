import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFutanariXXXSpider(BaseSceneScraper):
    name = 'FutanariXXX'
    network = 'Futanari XXX'
    parent = 'Futanari XXX'
    site = 'Futanari XXX'

    start_urls = [
        'https://futanari.xxx',
    ]

    selector_map = {
        'title': '//h1/text()[1]',
        'description': '//h3[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "tagsmodel")]/a/text()',
        'tags': '//h3[contains(text(), "Description")]/following-sibling::div[contains(@class, "Cats")]//a/text()',
        'duration': '//div[@class="duration"]/text()',
        'director': '//div[contains(@class, "director")]//a/text()',
        'trailer': '//video[@id="singlepreview"]/source/@src',
        'external_id': r'.*/(.*)/',
        'pagination': '/all-videos/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        id = response.xpath('//script[contains(@type, "application/json") and contains(@class, "gdrts")]/text()').get()
        id = re.search(r'item_id.*?(\d+),\"nonce', id).group(1)
        return str(id)
