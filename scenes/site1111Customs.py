import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Site1111CustomsXXXSpider(BaseSceneScraper):
    name = '1111CustomsXXX'
    site = '1111CustomsXXX'
    parent = '1111CustomsXXX'
    network = '1111CustomsXXX'

    start_urls = [
        'https://www.1111customsxxx.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block"]//span[contains(@class, "update_title")]/text()',
        'description': '//div[@class="update_block"]//span[contains(@class, "update_description")]/text()',
        'date': '//div[@class="update_block"]//span[contains(@class, "availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_block"]//div[@class="update_image"]/a[contains(@href, "updates")]/img/@src0_3x|//div[@class="update_block"]//div[@class="update_image"]/a[contains(@href, "updates")]/img/@src0_2x|//div[@class="update_block"]//div[@class="update_image"]/a[contains(@href, "updates")]/img/@src0_1x',
        'performers': '//div[@class="update_block"]//span[contains(@class, "update_models")]/a/text()',
        'tags': '//div[@class="update_block"]//span[contains(@class, "update_tags")]/a/text()',
        'trailer': '//div[@class="update_image"]/a[contains(@onclick, "mp4")][1]/@onclick',
        're_trailer': r'[\'\"](/.*?)[\'\"]',
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
            duration = re.sub(r'[^a-z0-9]', "", duration.replace("&nbsp;", "").lower())
            minutes = 0
            seconds = 0

            minutes = re.search(r'(\d+)min', duration)
            if minutes:
                minutes = int(minutes.group(1)) * 60
            else:
                minutes = 0

            seconds = re.search(r'(\d+)sec', duration)
            if seconds:
                seconds = int(seconds.group(1))
            else:
                seconds = 0
            return str(minutes + seconds)
        return None
