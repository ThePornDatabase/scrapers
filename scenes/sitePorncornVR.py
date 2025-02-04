import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePorncornVRSpider(BaseSceneScraper):
    name = 'PorncornVR'
    network = 'PorncornVR'
    parent = 'PorncornVR'
    site = 'PorncornVR'

    start_urls = [
        'https://porncornvr.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "collapse-content-wrapper")]/div[1]//text()',
        'date': '//i[contains(@class, "calendar")]/../following-sibling::strong/text()',
        'image': '//dl8-video/@poster',
        'performers': '//text()[contains(., "Starring:")]/following-sibling::a/text()',
        'tags': '//text()[contains(., "Tags:")]/following-sibling::a/text()',
        'duration': '//i[contains(@class, "clock")]/following-sibling::span[1]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/scenes/?page=%s&flt=new',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="panel"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "PorncornVR"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)

        return performers_data
