import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTaraTaintonSpider(BaseSceneScraper):
    name = 'TaraTainton'
    site = 'Tara Tainton'
    parent = 'Tara Tainton'
    network = 'Tara Tainton'

    start_urls = [
        'https://www.taratainton.com'
    ]

    selector_map = {
        'title': '//article/h1/text()',
        'description': '//article/p/text()',
        'date': '//article/div[@class="theDate"]/text()',
        'date_formats': ['%d %B %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[@class="tags"]/a/text()',
        'trailer': '//video/source/@src',
        'type': 'Scene',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/video/page/%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="homeEntry"]/h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Tara Tainton']

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = response.xpath('//div[@class="videoShow"]/img/@src')
            if image:
                image = self.format_link(response, image.get())

        if image:
            return image
        return ""
