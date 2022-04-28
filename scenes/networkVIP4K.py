import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkVIP4KSpider(BaseSceneScraper):
    name = 'VIP4K'
    network = 'VIP 4K'

    start_urls = [
        'https://vip4k.com',
    ]

    selector_map = {
        'title': '//h1[@class="player-description__title"]/text()',
        'description': '//div[@class="player-description__text"]/text()',
        'date': '//div[@class="player-description__additional"]/ul/li[@class="player-additional__item"][2]/span/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//picture[@class="player-item__inner"]//img/@data-src',
        'performers': '//div[@class="player-description__line"]/a/div[@class="model__name"]/text()',
        'tags': '//div[@class="player-description__tags"]/div/a/text()',
        'trailer': '',
        'external_id': r'videos/(\d+)',
        'pagination': '/en/videos/publish/all/all/all/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[@class="grid__item"]/div[@class="item"]')
        for scene in scenes:
            trailer = response.xpath('.//video/source/@src')
            if trailer:
                trailer = trailer.get()
            else:
                trailer = None
            scene = scene.xpath('./a[@class="item__main"]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'trailer': trailer})

    def get_site(self, response):
        site = response.xpath('//div[@class="player-description__additional"]/ul/li[@class="player-additional__item"][1]/a/text()')
        if site:
            site = site.get().strip()
        else:
            site = "VIP 4K"
        if site == "Sis":
            site = "Sis Porn"
        return site

    def get_parent(self, response):
        parent = response.xpath('//div[@class="player-description__additional"]/ul/li[@class="player-additional__item"][1]/a/text()')
        if parent:
            parent = parent.get().strip()
        else:
            parent = "VIP 4K"
        if parent == "Sis":
            parent = "Sis Porn"
        return parent
