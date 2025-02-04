import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJulieGingerSpider(BaseSceneScraper):
    name = 'JulieGinger'
    site = 'Julie Ginger'
    parent = 'Julie Ginger'
    network = 'Julie Ginger'

    start_urls = [
        'https://julieginger.com'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//img[contains(@class, "large_update_thumb")]/@src0_3x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            meta['id'] = re.search(r'-(\d+)', scene.xpath('./a[1]/img/@id').get()).group(1)
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
