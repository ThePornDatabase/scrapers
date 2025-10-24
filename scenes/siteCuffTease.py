import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCuffTeaseSpider(BaseSceneScraper):
    name = 'CuffTease'
    network = 'CuffTease'
    parent = 'CuffTease'
    site = 'CuffTease'

    start_urls = [
        'https://www.cufftease.com',
    ]

    selector_map = {
        'title': '//h3[contains(@class, "heading-title")]/text()',
        'description': '//h3[contains(@class, "heading-title")]/following-sibling::p[1]/text()',
        'date': '//time/@datetime',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class, "blog-wrap")]/div[1]/img/@src',
        'performers': '//h3[contains(@class, "heading-title")]/following-sibling::div[contains(@class, "post-tags")]/a[@rel="tag"]/text()',
        'external_id': r'',
        'pagination': '/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "blog-child-wrap")]')
        for scene in scenes:
            sceneid = scene.xpath('./@id').get()
            meta['id'] = re.search(r'-(\d+)', sceneid).group(1)
            scene = scene.xpath('.//h3/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Bondage']

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = self.get_network(response)
                perf['site'] = self.get_network(response)
                performers_data.append(perf)
        return performers_data
