import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGoonMuseSpider(BaseSceneScraper):
    name = 'GoonMuse'
    site = 'GoonMuse'
    parent = 'GoonMuse'
    network = 'GoonMuse'

    start_urls = [
        'https://www.goonmuse.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"update_description")]/text()',
        'date': '//span[contains(@class,"availdate")]/text()[1]',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img[contains(@class, "large_update_thumb")]/@src0_3x|//div[@class="update_image"]/a/img[contains(@class, "large_update_thumb")]/@src0_2x|//div[@class="update_image"]/a/img[contains(@class, "large_update_thumb")]/@src0_1x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'trailer': '',
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
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]+', '', duration.strip().lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
