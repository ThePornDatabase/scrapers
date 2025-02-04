import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDrRideoutSpider(BaseSceneScraper):
    name = 'DrRideout'
    site = 'DrRideout'
    parent = 'DrRideout'
    network = 'DrRideout'

    start_urls = [
        'https://drrideout.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"update_description")]/text()',
        'date': '//span[@class="availdate"]/text()[1]',
        'date_formats': ['%m/%d/%Y'],
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            image = scene.xpath('.//img/@src0_4x')
            if not image:
                image = scene.xpath('.//img/@src0_3x')
            if not image:
                image = scene.xpath('.//img/@src0_2x')
            if not image:
                image = scene.xpath('.//img/@src0_1x')

            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//text()[contains(., "minutes") and contains(., "video")]')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
