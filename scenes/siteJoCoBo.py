import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJoCoBoSpider(BaseSceneScraper):
    name = 'JoCoBo'
    network = 'JoCoBo'
    parent = 'JoCoBo'
    site = 'JoCoBo'

    start_urls = [
        'https://www.jocobo.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//i[contains(@class, "calendar")]/following-sibling::span[1]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//i[contains(@class, "fa-users")]/following-sibling::span[1]/a/text()',
        'duration': '//div[@class="view-card" and contains(text(), "min")]//text()[contains(., ":")]',
        'external_id': r'',
        'pagination': '/collections/page/%s?media=video',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card"]/a[1]/@href').getall()
        uuid_pattern = r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'
        for scene in scenes:
            uuid_match = re.search(uuid_pattern, scene)
            if uuid_match:
                meta['id'] = uuid_match.group(0)
            else:
                meta['id'] = re.search(r'.*/(.*?)$', scene).group(1)
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = []
        scene_tags = response.xpath('//i[contains(@class, "fa-tags")]/following-sibling::span[1]/a/text()')
        if scene_tags:
            tags = scene_tags.getall()

        keywords = []
        scene_keywords = response.xpath('//div[contains(@class, "tags")]/a/text()')
        if scene_keywords:
            keywords = scene_keywords.getall()

        tags = tags + keywords

        return list(map(lambda x: string.capwords(x.strip()), tags))
