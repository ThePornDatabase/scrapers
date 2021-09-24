import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PurgatoryXSpider(BaseSceneScraper):
    name = "PurgatoryX"
    network = 'Radical Entertainment'
    parent = "PurgatoryX"

    start_urls = [
        'https://tour.purgatoryx.com'
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//meta[@name="description"]/@content',
        'date': "//span[@class='date']/text()",
        'image': '//div[contains(@class,"player-wrap")]/*/@poster',
        'performers': '//div[@class="model-wrap"]/ul/li/h5/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': 'view\\/(\\d+)\\/',
        'trailer': '//a[contains(@class,"download-trailer")]/@href',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="details-wrap"]/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//p[@class="series"]/span/text()').get().strip()
        if not site:
            site = "PurgatoryX"
        return site

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).get()
            if "," in tags:
                tags = tags.split(",")
            return list(map(lambda x: x.strip(), tags))
        return []
