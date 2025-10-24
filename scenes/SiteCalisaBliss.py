import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCalisaBlissSpider(BaseSceneScraper):
    name = 'CalisaBliss'
    network = 'Calisa Bliss'
    parent = 'Calisa Bliss'
    site = 'Calisa Bliss'

    start_urls = [
        'https://calisabliss.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()[1]',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a[contains(@href, "/updates/")][1]/img/@src0_4x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'tload\(\'(.*\.mp4)',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "update_counts") and contains(text(), "min")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "")
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = ""
        return image
