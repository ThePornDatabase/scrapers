import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNextdoorSinsSpider(BaseSceneScraper):
    name = 'NextdoorSins'
    network = 'Nextdoor Sins'
    parent = 'Nextdoor Sins'
    site = 'Nextdoor Sins'

    start_urls = [
        'https://www.nextdoorsins.com',
    ]

    selector_map = {
        'title': '//span[contains(@class, "title")]/text()',
        'description': '//span[contains(@class, "description")]/text()',
        'date': '//span[@class="availdate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '',
        'performers': '',
        'tags': '//span[@class="update-tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movie-holder"]/a/@href|//div[@class="video"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = response.xpath('//div[@class="large-image-holder"]/a/img/@src0_2x')
        if not image:
            image = response.xpath('//div[@class="large-image-holder"]/a/img/@src0_1x')

        if image:
            image = "https://www.nextdoorsins.com/tour/" + image.get()
            return image

        return ''
