import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrokenLatinaWhoresSpider(BaseSceneScraper):
    name = 'BrokenLatinaWhores'
    network = 'Broken Latina Whores'
    parent = 'Broken Latina Whores'
    site = 'Broken Latina Whores'

    start_urls = [
        'https://www.brokenlatinawhores.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class, "description")]//text()',
        'date': '//span[contains(@class, "availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content|//meta[@property="twitter:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'trailer': '//div[@class="update_image"]/a[contains(@onclick, "tload")][1]/@onclick',
        're_trailer': r'(/.*\.mp4)',
        'external_id': r'.*/(.*)\.html',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Latina")
        return tags
