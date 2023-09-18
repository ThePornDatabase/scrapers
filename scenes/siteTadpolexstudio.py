import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTadpolexstudioSpider(BaseSceneScraper):
    name = 'Tadpolexstudio'
    network = 'Tadpolexstudio'
    parent = 'Tadpolexstudio'
    site = 'Tadpolexstudio'

    start_urls = [
        'https://www.tadpolexstudio.com',
    ]

    selector_map = {
        'title': '//div[@class="video-player"]/div[@class="title-block"]/h2[@class="section-title"]/text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::text()',
        'date': '//div[@class="update-info-block"]//i[contains(@class,"fa-calendar")]/following-sibling::strong/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-thumb"]//img/@src0_1x',
        'performers': '//div[contains(@class,"models-list-thumbs")]//a//span/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//div[@class="update-info-block"]//i[contains(@class,"fa-clock")]/following-sibling::strong/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"videothumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
