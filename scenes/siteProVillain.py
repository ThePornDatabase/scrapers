import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteProVillainSpider(BaseSceneScraper):
    name = 'ProVillain'
    network = 'ProVillain'
    parent = 'ProVillain'
    site = 'ProVillain'

    start_urls = [
        'https://provillain.com',
    ]

    selector_map = {
        'title': '//h3[contains(@class, "page-title")]/text()',
        'description': '//h3[contains(@class, "page-title")]/following-sibling::p/following-sibling::p[not(contains(text(), "Running time")) and not(contains(text(), "Price"))]/text()',
        'image': '//h3[contains(@class, "page-title")]/following-sibling::p[1]//img/@src',
        'duration': '//h3[contains(@class, "page-title")]/following-sibling::p[1]/following-sibling::p[contains(text(), "Running time")][1]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/provillain/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article')
        for scene in scenes:
            scenedate = scene.xpath('.//time/@datetime')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    meta['date'] = scenedate.group(1)

            image = scene.xpath('.//img/@src')
            if image:
                meta['orig_image'] = image.get()

            meta['id'] = scene.xpath('./@id').get()
            meta['id'] = re.search(r'-(\d+)', meta['id']).group(1)

            scene = scene.xpath('./h2/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['BDSM', 'Bondage', 'Damsel in Distress', 'Gag', 'Domination', 'Submissive', 'Slave Training', 'Bondage Sex']

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if image in response.url:
            image = meta['orig_image']
        return image
