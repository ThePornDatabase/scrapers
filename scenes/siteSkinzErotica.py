import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSkinzEroticaSpider(BaseSceneScraper):
    name = 'SkinzErotica'
    network = 'SkinzErotica'
    parent = 'SkinzErotica'
    site = 'SkinzErotica'

    start_urls = [
        'https://www.skinzerotica.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "featuring")]/ul/li[contains(@class, "update_models")]/a/text()',
        'tags': '//div[contains(@class, "featuring")]//a[contains(@href, "categories")]/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            meta['id'] = re.search(r'b(\d+)_', sceneid).group(1)
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//text()[contains(., "of video") and contains(., "min")]')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_image(self, response):
        image = super().get_image(response)
        return image.replace("-1x", "-4x")
