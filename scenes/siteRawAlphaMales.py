import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRawAlphaMalesSpider(BaseSceneScraper):
    name = 'RawAlphaMales'
    network = 'Raw Alpha Males'
    parent = 'Raw Alpha Males'
    site = 'Raw Alpha Males'

    start_urls = [
        'https://www.rawalphamales.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-container")]/h1/small/following-sibling::text()',
        'description': '//div[contains(@class,"video-container")]//div[@class="row"]/div/p/text()',
        'date': '//div[contains(@class,"video-container")]/h1/small/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//script[contains(text(), "playlist")]/text()',
        're_image': r'image:.*?\'(.*?)\'',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/video/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-container")]/div/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']

    def get_image(self, response):
        image = super().get_image(response)
        if not re.search(r'com/.*(\.\w{3,4})', image):
            image = response.xpath('//div[contains(@class,"video-container")]/div/div[1]/img/@data-original')
            if image:
                image = self.format_link(response, image.get())
        return image
