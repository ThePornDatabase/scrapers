import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRHushSpider(BaseSceneScraper):
    name = 'VRHush'
    network = 'VR Hush'
    parent = 'VR Hush'
    site = 'VR Hush'

    start_urls = [
        'https://vrhush.com',
    ]

    selector_map = {
        'title': '//h1[@class="latest-scene-title"]/text()',
        'description': '//span[contains(@class,"full-description")]/text()',
        'date': '//div[contains(@class,"latest-scene-meta-1")]/div[1]/text()',
        'date_formats': ['%b %d, %y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h5/a[contains(@href, "/models/")]/text()',
        'tags': '//p[@class="tag-container"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'scenes/(.*?)_',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h4[@class="latest-scene-title"]/../@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Virtual Reality")
        tags.append("VR")
        return tags
