import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class GirlsOutWestSpider(BaseSceneScraper):
    name = 'GirlsOutWest'
    network = "GirlsOutWest"
    parent = "GirlsOutWest"

    start_urls = [
        'https://tour.girlsoutwest.com'
    ]

    selector_map = {
        'title': '//div[@class="vpTitle"]/h1/text()',
        'description': '//div [@class="description"]/p//text()',
        'date': '//h5[contains(text(), "Added:")]/following-sibling::p/text()',
        'date_formats': ['%B %d, %Y'],
        'duration': '//h5[contains(text(), "Runtime:")]/following-sibling::text()',
        're_duration': r'(\d{1,2}\:?\d{1,2}\:\d{1,2})',
        'image': '//div[@class="player-thumb"]//img/@src0_3x|//div[@class="player-thumb"]//img/@src0_2x|//div[@class="player-thumb"]//img/@src0_1x',
        'performers': '//h5[contains(text(), "Featuring:")]/following-sibling::ul/li/a/text()',
        'tags': '//h5[contains(text(), "Tags:")]/following-sibling::ul/li/a/text()',
        'external_id': r'/trailers/(.*).ht',
        'trailer': '',
        'pagination': '/categories/Movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"videothumb")]/a/@href|//div[contains(@class,"iLScenePic")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        scene_id = super().get_id(response)
        return scene_id.lower()
