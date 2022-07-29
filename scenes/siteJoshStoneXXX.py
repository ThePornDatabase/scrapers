import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJoshStoneXXXSpider(BaseSceneScraper):
    name = 'JoshStoneXXX'
    network = 'Josh Stone Productions'
    parent = 'Josh Stone XXX'
    site = 'Josh Stone XXX'

    start_urls = [
        'https://www.joshstonexxx.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[@class="availdate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="update_block_info"]/span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'trailer': '//div[@class="update_image"]/a[contains(@onclick, "trailer")][1]/@onclick',
        're_trailer': r'(trailer.*\.mp4)',
        'external_id': r'.*/(.*?)\.html',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
