import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCocksureMenSpider(BaseSceneScraper):
    name = 'CocksureMen'
    network = 'Jake Cruise Media'
    parent = 'Cocksure Men'
    site = 'Cocksure Men'

    start_urls = [
        'https://www.cocksuremen.com',
    ]

    selector_map = {
        'title': '//div[@class="videoleft"]/h3/text()',
        'description': '//div[@class="videoleft"]//div[@class="aboutvideo"]/p/text()',
        'date': '',
        'image': '//script[contains(text(), video_content)]/text()',
        're_image': r'poster=[\'\"](.*?)[\'\"]',
        'performers': '//ul[@class="featuredModels"]/li/a//span/text()',
        'tags': '',
        'duration': '//div[@class="videoleft"]/h4[1]/text()',
        'trailer': '//script[contains(text(), video_content)]/text()',
        're_trailer': r'video src=[\'\"](.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"sexycock_img")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
