import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNylonUpSpider(BaseSceneScraper):
    name = 'NylonUp'
    network = 'Nylon Up'
    parent = 'Nylon Up'
    site = 'Nylon Up'

    start_urls = [
        'https://www.nylonup.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/p/text()',
        'date': '//div[contains(@class, "videoInfo")]/p/span[contains(text(), "Date")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "poster=")]/text()',
        're_image': r'poster=\s?\"(.*\.jpg)',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[@class="label"]/following-sibling::li/a[contains(@href, "/categories/")]/text()',
        'external_id': r'trailers/(.*?)\.html',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
