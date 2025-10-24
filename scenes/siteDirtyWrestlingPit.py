import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDirtyWrestlingPitSpider(BaseSceneScraper):
    name = 'DirtyWrestlingPit'
    network = 'DirtyWrestlingPit'
    parent = 'DirtyWrestlingPit'
    site = 'DirtyWrestlingPit'

    start_urls = [
        '',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
