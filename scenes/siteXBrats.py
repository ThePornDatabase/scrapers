import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXBratsSpider(BaseSceneScraper):
    name = 'XBrats'
    network = 'XBrats'
    parent = 'XBrats'
    site = 'XBrats'

    start_urls = [
        'https://xbrats.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()[1]',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a[1]/img/@src0_3x',
        'performers': '//span[contains(@class,"tour_update_models")]/a/text()[1]',
        'tags': '//span[contains(@class,"update_tags")]/a/text()[1]',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts" and contains(text(), "min") and contains(text(), "video")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "")
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
