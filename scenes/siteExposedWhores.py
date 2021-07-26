import dateparser
import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class ExposedWhoresSpider(BaseSceneScraper):
    name = 'ExposedWhores'
    network = 'Exposed Whores'
    parent = 'Exposed Whores'

    start_urls = [
        'https://exposedwhores.com'
    ]

    selector_map = {
        'title': '//span[contains(@class,"update_title")]/text()',
        'description': '//span[contains(@class,"update_title")]/text()', #No description on site, just using title for filler
        'date': '//span[contains(@class,"availdate")]/text()',
        'image': '//img[contains(@class,"large_update_thumb")]/@src',
        'performers': '//div[@class="update_block_info"]/span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'external_id': '\/updates\/(.+)\.html',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        'pagination': '/new-tour/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta={'site': 'Exposed Whores'})

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search('tload\(\'(.*)\'\)', trailer).group(1)
                if trailer:
                    trailer = "https://exposedwhores.com" + trailer
                    return trailer
        return ''


    def get_description(self, response):

        description = self.process_xpath(
            response, self.get_selector_map('description')).get()

        if description is not None:
            return description.replace('\r\n', '  ').strip()
        return ""
