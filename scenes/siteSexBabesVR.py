import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSexBabesVRSpider(BaseSceneScraper):
    name = 'SexBabesVR'
    network = 'SexBabesVR'
    parent = 'SexBabesVR'
    site = 'SexBabesVR'
    start_urls = [
        'https://sexbabesvr.com',
    ]

    selector_map = {
        'title': '//script[contains(text(), "VideoObject")]/text()',
        're_title': r'\"VideoObject\",\"name\":.*?[\'\"](.*?)[\'\"]',
        'description': '//script[contains(text(), "VideoObject")]/text()',
        're_description': r'\"description\".*?\"(.*?)\",',
        'date': '//script[contains(text(), "VideoObject")]/text()',
        're_date': r'\"uploadDate\".*?\"(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "video-detail")]/a[contains(@href, "/model/")]/text()',
        'tags': '//div[contains(@class, "tags")]/a[@class="tag"]/text()',
        'duration': '//script[contains(text(), "VideoObject")]/text()',
        're_duration': r'\"duration\".*?\"(.*?)\"',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/vr-porn-videos/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "item video-container")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if 'VR' not in tags:
            tags.append('VR')
            tags.append('Virtual Reality')
        return tags