import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteThatFetishGirlSpider(BaseSceneScraper):
    name = 'ThatFetishGirl'
    network = 'That Fetish Girl'
    site = 'That Fetish Girl'
    parent = 'That Fetish Girl'

    start_urls = [
        'https://thatfetishgirl.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block"]//span[@class="update_title"]/text()',
        'description': '//div[@class="update_block"]//span[contains(@class,"update_description")]/text()',
        'date': '//div[@class="update_block"]//span[contains(@class,"availdate")]/text()[1]',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]//img[contains(@class, "large_update")]/@src',
        'performers': '//div[@class="update_block"]//span[contains(@class,"update_models")]/a/text()',
        'tags': '//div[@class="update_block"]//span[contains(@class,"update_tags")]/a/text()',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'\([\'\"](.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "update_counts")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("\r", "").replace("\n", "").replace("\t", "").replace("&nbsp;", " ").replace("\xa0", " ").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
