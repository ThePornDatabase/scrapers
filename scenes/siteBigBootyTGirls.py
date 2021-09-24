import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBigBootyTGirlsSpider(BaseSceneScraper):
    name = 'BigBootyTGirls'
    network = 'Big Booty Tgirls'

    start_urls = [
        'https://www.bigbootytgirls.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"titleBlock2")]/h3/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"availdate")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        're_trailer': r'(trailer.*\.mp4)',
        'pagination': '/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]//h5/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        trailer = self.format_link(response, trailer)
        return trailer

    def get_site(self, response):
        return "Big Booty Tgirls"

    def get_parent(self, response):
        return "Big Booty Tgirls"
