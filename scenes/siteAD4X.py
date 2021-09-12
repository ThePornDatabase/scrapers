import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AD4XSpider(BaseSceneScraper):
    name = "AD4X"
    network = 'Radical Entertainment'

    start_urls = [
        'https://tour.ad4x.com'
    ]

    selector_map = {
        'title': '//h2[contains(@class,"content-title")]/text()',
        'description': '',
        'date': '//span[@class="date"]/text()',
        'image': '//video/@poster',
        'performers': '//p[@class="models mb-0"]/a/text()',
        'tags': '',
        'external_id': 'videos\\/(\\d+)\\/',
        'trailer': '//a[contains(@class,"download-trailer")]/@href',
        'pagination': '/tour/en/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).get()
            if "," in tags:
                tags = tags.split(",")
            return list(map(lambda x: x.strip(), tags))
        return []

    def get_performers(self, response):
        performers = self.process_xpath(
            response, self.get_selector_map('performers')).getall()
        return list(map(lambda x: x.strip().title(), performers))

    def get_description(self, response):
        return ''
