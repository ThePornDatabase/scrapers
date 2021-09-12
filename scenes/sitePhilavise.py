import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PhilaviseSpider(BaseSceneScraper):
    name = 'Philavise'
    network = 'Philavise'
    parent = 'Philavise'

    start_urls = [
        'https://www.philavise.com'
    ]

    selector_map = {
        'title': '//span[contains(@class,"update_title")]/text()',
        'description': '//span[contains(@class,"update_description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//img[contains(@class,"large_update_thumb")]/@src',
        'performers': '//span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'external_id': r'\/updates\/(.+)\.html',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta={'site': 'Philavise'})

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search(r'tload\(\'(.*)\'\)', trailer).group(1)
                if trailer:
                    trailer = "https://www.philavise.com" + trailer
                    return trailer
        return ''

    def get_description(self, response):

        description = self.process_xpath(
            response, self.get_selector_map('description')).get()

        if description is not None:
            return description.replace('\r\n', '  ').strip()
        return ""
