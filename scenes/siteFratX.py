import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFratXSpider(BaseSceneScraper):
    name = 'FratX'
    network = 'FratX'
    parent = 'FratX'
    site = 'FratX'

    start_urls = [
        'https://fratx.com',
    ]

    selector_map = {
        'title': '//div[@class="name"]/span/text()',
        'description': '//div[@class="VideoDescription"]/text()',
        're_description': r'.*?, \d{4} - (.*)',
        'date': '//div[@class="VideoDescription"]/text()',
        're_date': r'(\w+ \d{1,2}\w{2}?, \d{4})',
        'image': '//video/@poster',
        'performers': '//ul[@class="ModelNames"]/li/a/text()',
        'tags': '//div[@class="VideoTagsWrap"]/a/span/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'id=(\d+)',
        'pagination': '/index.php?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="video-thumb-wrap"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.extend(['College', 'Gay'])
        return tags
    
    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            perf = {}
            perf['name'] = string.capwords(performer)
            perf['extra'] = {'gender': "Male"}
            perf['site'] = 'FratX'
            performers_data.append(perf)
        return performers_data
            