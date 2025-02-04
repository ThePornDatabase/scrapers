import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSpankingStraightBoysSpider(BaseSceneScraper):
    name = 'SpankingStraightBoys'
    site = 'Spanking Straight Boys'
    parent = 'Spanking Straight Boys'
    network = 'Spanking Straight Boys'

    start_urls = [
        'https://spankingstraightboys.com'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img/@src0_1x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'duration': '',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'[\'\"](.*\.mp4)',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/tour/categories/updates_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
