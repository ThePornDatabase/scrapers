import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRadicalJizzlamSpider(BaseSceneScraper):
    name = 'RadicalJizzlam'
    site = 'Radical Jizzlam'
    parent = 'Radical Jizzlam'
    network = 'Radical Jizzlam'

    start_urls = [
        'https://www.radicaljizzlam.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h1/following-sibling::p[1]//text()',
        'date': '',
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': 'src0_3x.*?(http.*?)[\'\"]',
        'performers': '',
        'tags': '//li[@class="label"]/following-sibling::li/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*)?\.htm',
        'pagination': '/tour/updates/page_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-video")]/div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
