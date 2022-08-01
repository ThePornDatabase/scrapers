import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteElegantAngelSpider(BaseSceneScraper):
    name = 'ElegantAngel'
    network = 'Elegant Angel'
    parent = 'Elegant Angel'
    site = 'Elegant Angel'

    start_urls = [
        'https://www.elegantangel.com',
    ]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//h1[@class="description"]/text()',
        'date': '//span[contains(text(), "Released:")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]/a/span/span/text()',
        'tags': '//span[contains(text(), "Tags:")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'/(\d{2,8})/',
        'pagination': '/tour?page=%s&hybridview=member'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[@class="scene-update"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
