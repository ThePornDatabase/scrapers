import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBondageCafeSpider(BaseSceneScraper):
    name = 'BondageCafe'
    network = 'Bondage Cafe'

    start_urls = [
        'https://www.bondagecafe.com/',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()',
        'image': '//img[contains(@class,"large_update_thumb")]/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'.*/(w.*?-\d{2,5})-',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'\'(.*\.mp4)\'',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Bondage Cafe"

    def get_parent(self, response):
        return "Bondage Cafe"
