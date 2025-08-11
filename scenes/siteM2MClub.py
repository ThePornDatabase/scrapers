import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteM2MClubSpider(BaseSceneScraper):
    name = 'M2MClub'
    network = 'M2MClub'
    parent = 'M2MClub'
    site = 'M2MClub'

    start_urls = [
        'https://www.m2mclub.com',
    ]

    selector_map = {
        'title': '//span[contains(@class, "update_title")]/text()',
        'description': '//span[contains(@class, "update_description")]/text()',
        'date': '//span[contains(@class, "availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[contains(@class, "update_image")]/a/img[contains(@class, "large_update_thumb")]/@src0_1x',
        'performers': '//span[contains(@class, "update_models")]/a/text()',
        'tags': '//span[contains(@class, "update_tags")]/a/text()',
        'trailer': '//div[contains(@class, "update_image")]/a[1]/@onclick',
        're_trailer': r'\([\'\"](.*?)[\'\"]\)',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "updateItem")]')
        for scene in scenes:
            image = scene.xpath('.//img/@src0_4x')
            if image:
                image = self.format_link(response, image.get())
                image_blob = self.get_image_blob_from_link(image)
                if not image_blob:
                    image = image.replace("1-4x", "1-3x")
                    image_blob = self.get_image_blob_from_link(image)
                    if not image_blob:
                        image = image.replace("1-3x", "1-2x")
                        image_blob = self.get_image_blob_from_link(image)
                        if not image_blob:
                            image = image.replace("1-2x", "1")
                            image_blob = self.get_image_blob_from_link(image)

            if image_blob:
                meta['image'] = image
                meta['image_blob'] = image_blob

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(text(), "of video")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "").replace(" ", "").strip().lower()
            duration = re.search(r'(\d+)ofvideo', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Gay")
        return tags

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
