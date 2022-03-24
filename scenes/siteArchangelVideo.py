import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteArchangelVideoSpider(BaseSceneScraper):
    name = 'ArchangelVideo'
    network = 'Arch Angel'
    parent = 'Arch Angel'
    site = 'Arch Angel'

    start_urls = [
        'https://archangelvideo.com',
    ]

    selector_map = {
        'title': '//div[@class="bodyInnerArea"]/div/div/h2/i[@class="fa fa-film"]/following-sibling::text()',
        'description': '',
        'date': '//div[@class="info"]/p/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="info"]//a/text()',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "video")]/text()',
        're_trailer': r'(http.*?\.mp4)',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
