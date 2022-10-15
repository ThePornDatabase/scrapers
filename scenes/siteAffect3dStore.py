import re
import json
import scrapy
# ~ from helpers.scrapy_flare.request import FlareRequest
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAffect3dStoreSpider(BaseSceneScraper):
    name = 'Affect3dStore'
    network = 'Affect3dStore'
    parent = ''
    site = ''

    custom_settings = {'DOWNLOADER_MIDDLEWARES': {'tpdb.helpers.scrapy_flare.middleware.FlareMiddleware': 543}}

    start_urls = [
        'https://affect3dstore.com',
    ]

    selector_map = {
        'title': '//h1[@class="page-title"]/span/text()',
        'description': '//div[@itemprop="description"]/p/text()',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/animation/short-clips.html?p=%s'
    }

    def get_scenes(self, response):
        print(response.text)
        scenes = response.xpath('//div[@class="product-info"]/div/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.FlareRequest(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        print(response.text)
