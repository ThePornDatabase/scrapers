import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLovinglyHandmadePornographySpider(BaseSceneScraper):
    name = 'LovinglyHandmadePornography'
    network = 'LovinglyHandmadePornography'
    parent = 'LovinglyHandmadePornography'
    site = 'LovinglyHandmadePornography'

    start_urls = [
        'https://lovinglyhandmadepornography.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "text-2xl")]/text()',
        'description': '//h1/following-sibling::div[contains(@class, "prose")][1]/text()',
        'date': '//text()[contains(., "Published:")]',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[@id="video_container"]/video/@poster',
        'performers': '//a[contains(@href, "/tagged") and not(contains(@class, "text-["))]/text()',
        'tags': '//a[contains(@href, "/tagged") and contains(@class, "text-[")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/updates?pg=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        # ~ print(response.text)
        meta = response.meta
        scenes1 = response.xpath('//video/ancestor::a[1]/@href').getall()
        scenes2 = response.xpath('//img[contains(@class, "gif_thumb")]/ancestor::a[1]/@href').getall()
        scenes = list(set(scenes1 + scenes2))

        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        return title.strip().strip('"')

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

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "hevc" not in tag.lower():
                if not re.search(r'(\d{3,4})', tag):
                    tags2.append(tag)
        return tags2
