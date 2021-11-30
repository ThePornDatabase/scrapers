import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBathroomCreeperSpider(BaseSceneScraper):
    name = 'BathroomCreepers'
    network = 'Bathroom Creepers'
    parent = 'Bathroom Creepers'
    site = 'Bathroom Creepers'

    start_urls = [
        'https://www.bathroomcreepers.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '//div[@class="videoInfo clear"]/comment()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="player-thumb"]/img/@src0_3x',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href, "/categories/")]/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/creeper/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_image(self, response):
        image = response.xpath('//div[@class="player-thumb"]/img/@src0_3x')
        if not image:
            image = response.xpath('//div[@class="player-thumb"]/img/@src0_2x')
        if not image:
            image = response.xpath('//div[@class="player-thumb"]/img/@src0_1x')
        if image:
            return self.format_link(response, image.get())
        return None
