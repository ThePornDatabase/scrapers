import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteMariskaXSpider(BaseSceneScraper):
    name = 'MariskaX'
    network = 'Mariska X'


    start_urls = [
        'https://tour.mariskax.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//span[@class="post-date"]/text()',
        'image': '//video/@poster',
        'performers': '//div[@class="content-meta"]/h4[@class="models"]/a/text()',
        'tags': '',
        'external_id': 'view\/(\d+)\/',
        'trailer': '//video/source/@src',
        'pagination': '/scenes?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h3[@class="title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Mariska X"

    def get_parent(self, response):
        return "Mariska X"
        
    def get_description(self, response):
        return ''
        
