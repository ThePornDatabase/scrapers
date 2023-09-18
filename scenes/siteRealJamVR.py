import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRealJamVRSpider(BaseSceneScraper):
    name = 'RealJamVR'
    network = 'realjamvr'
    parent = 'realjamvr'
    site = 'realjamvr'

    start_urls = [
        'https://realjamvr.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"opacity-75")]/text()',
        'date': '//i[contains(@class, "bi-calendar")]/../../strong/text()',
        'date_formats': ['%B %d, %Y'],
        'duration': '//i[contains(@class, "bi-clock-history")]/../../strong/text()',
        'image': '//dl8-video/@poster',
        'performers': '//div[contains(text(), "Starring")]/a/text()',
        'tags': '//div[contains(text(), "Tags")]/a/text()',
        'trailer': '',
        'external_id': r'/scene/(.*)',
        'pagination': '/scenes/?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="panel"]')
        for scene in scenes:
            trailer = scene.xpath('.//video/source/@src')
            if trailer:
                meta['trailer'] = trailer.get()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
