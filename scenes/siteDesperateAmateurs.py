import scrapy
import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDesperateAmateursSpider(BaseSceneScraper):
    name = 'DesperateAmateurs'
    network = 'Desperate Amateurs'
    parent = 'Desperate Amateurs'
    site = 'Desperate Amateurs'

    start_urls = [
        'https://www.desperateamateurs.com'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'date': '//span[@class="update_date"]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_table_right"]/div/a/img/@src0_3x|//div[@class="update_table_right"]/div/a/img/@src0_4x',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'trailer': '//div[@class="update_table_right"]/div/a[1]/@onclick',
        're_trailer': r'[\'\"](.*?.mp4)[\'\"]',
        'external_id': r'',
        'pagination': '/tour3/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./a[1]/@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), meta=meta, callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        if "tour3" not in image:
            image = image.replace(".com/content", ".com/tour3/content")
        return image
