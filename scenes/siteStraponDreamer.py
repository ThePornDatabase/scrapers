import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStraponDreamerSpider(BaseSceneScraper):
    name = 'StraponDreamer'
    network = 'StraponDreamer'
    parent = 'StraponDreamer'
    site = 'StraponDreamer'

    start_urls = [
        'https://mediastore.cloud',
    ]

    selector_map = {
        'title': '//div[contains(@class,"movie--info-title")]/text()',
        'description': '//div[contains(@class,"info-description")]//text()[not(contains(., "SHOW MORE"))]',
        'external_id': r'.*/(.*?)$',
        'pagination': '/content-A0007/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "grid-item")]/ancestor::a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        sceneid = self.get_id(response)
        if sceneid:
            image = f"https://assets.mediastore.cloud/sd_covers/{sceneid}-1080.jpg"
            if image:
                return self.format_link(response, image)
            return None
        
    def get_tags(self, response):
        return ['Strap-On', 'Pegging']

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "info-length")]/span[contains(text(), "minutes")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None    