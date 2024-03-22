import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMilfCandySpider(BaseSceneScraper):
    name = 'MilfCandy'
    network = 'Milf Candy'
    parent = 'Milf Candy'
    site = 'Milf Candy'

    start_urls = [
        'https://tour.milfcandy.com',
    ]

    selector_map = {
        'title': '//div[@class="bodyInnerArea"]/div[1]/div[contains(@class, "title clear")]/h2/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '//div[@class="info"]/p/text()[contains(., "Added")]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster.*?[\'\"](.*?)[\'\"]',
        'performers': '//div[@class="info"]/p[1]//a/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//div[@class="info"]/p/text()[contains(., "Runtime")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src.*?[\'\"](.*?)[\'\"]',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item item-video"]')
        for scene in scenes:
            sceneid = scene.xpath('.//img/@id').get()
            meta['id'] = re.search(r'-(\d+)', sceneid).group(1)

            scene = scene.xpath('./div[1]/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if "content" not in image:
            image = response.xpath('//div[@class="player-thumb"]//img/@src0_3x|//div[@class="player-thumb"]//img/@src0_2x|//div[@class="player-thumb"]//img/@src0_1x')
            if image:
                image = image.get()
                image = self.format_link(response, image)
        return image
