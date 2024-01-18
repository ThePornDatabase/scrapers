import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMonstersOfJizzSpider(BaseSceneScraper):
    name = 'MonstersOfJizz'
    network = 'Monsters Of Jizz'
    parent = 'Monsters Of Jizz'
    site = 'Monsters Of Jizz'

    start_urls = [
        'https://monstersofjizz.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block_info"]/span[contains(@class, "title")]/text()',
        'description': '//div[@class="update_block"]//span[contains(@class, "description")]/text()',
        'date': '//div[@class="update_block"]//span[contains(@class, "availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]//img[contains(@class, "large_update")]/@src0_2x|//div[@class="update_image"]//img[contains(@class, "large_update")]/@src0_3x|//div[@class="update_image"]//img[contains(@class, "large_update")]/@src0_4x',
        'performers': '//div[@class="update_block"]//span[contains(@class, "tour_update_models")]/a/text()',
        'tags': '//div[@class="update_block"]//span[contains(@class, "update_tags")]/a/text()',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'[\'\"](.*)[\'\"]',
        'external_id': r'updates/(.*)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        id = super().get_id(response)
        return id.lower()

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "").replace(" ", "").lower()
            duration = re.sub(r'[^a-z0-9]', '', duration)
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
        return duration
