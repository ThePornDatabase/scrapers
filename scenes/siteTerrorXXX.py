import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTerrorXXXSpider(BaseSceneScraper):
    name = 'TerrorXXX'
    network = 'Terror XXX'
    parent = 'Terror XXX'
    site = 'Terror XXX'

    start_urls = [
        'https://terrorxxx.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"title")]/span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(),"/trailers/")]',
        're_trailer': r'\"(/trailers.*?\.mp4)\"',
        'pagination': '/categories/Movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
