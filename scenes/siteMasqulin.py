import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMasqulinSpider(BaseSceneScraper):
    name = 'Masqulin'
    network = 'Masqulin'
    parent = 'Masqulin'
    site = 'Masqulin'

    start_urls = [
        'https://www.masqulin.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"gallery_info")]/h1/text()',
        'description': '//p[@class="update_description"]/text()',
        'date': '//span[@class="availdate" and not(contains(@style, "right"))]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@class="fullscreenTour"]/video-js/@poster',
        'performers': '//div[contains(@class, "gallery_info")]/p/span/a[contains(@href, "models")]/text()',
        'tags': '//a[@class="tagsVideoPage"]/text()',
        'duration': '//span[@class="availdate" and contains(@style, "right")]/text()',
        're_duration': r'(\d{1,2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateDetails"]/@onclick').getall()
        for scene in scenes:
            scene = re.search(r'(http.*\.\w{3,4})', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
