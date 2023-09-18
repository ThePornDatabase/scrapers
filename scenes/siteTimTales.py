import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTimTalesSpider(BaseSceneScraper):
    name = 'TimTales'
    network = 'Tim Tales'
    parent = 'Tim Tales'
    site = 'Tim Tales'

    start_urls = [
        'https://www.timtales.com',
    ]

    selector_map = {
        'title': '//div[@class="text"]/h1/text()',
        'description': '//div[contains(@class,"video-box")]/div/p[contains(@class, "bodytext")]/text()',
        'date': '//div[contains(@class,"video-box")]/div/p[@class="date"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[contains(@id, "video-") and contains(@class, "play-button")]/@style',
        're_image': r'(http.*?\.\w{3})\'',
        'performers': '//div[contains(@class,"video-box")]/div/p[@class="categories" and contains(text(), "Men")]/a/text()',
        'tags': '//div[contains(@class,"video-box")]/div/p[@class="categories"]/a/text()',
        'duration': '//div[contains(@class,"video-box")]/div/p[@class="date"]/text()',
        're_duration': r'(\d{1,2}:\d{2}(?::\d{2})?)',
        'trailer': '',
        'external_id': r'videos/(.*?)/',
        'pagination': '/videos/latest/page-%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-item")]')
        for scene in scenes:
            sceneid = scene.xpath('./div/@id')
            if sceneid:
                meta['id'] = re.search(r'-(\d+)', sceneid.get()).group(1)
            else:
                meta['id'] = None
            scene = scene.xpath('./div/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        performers = super().get_performers(response)
        for performer in performers:
            if performer in tags:
                tags.remove(performer)
        return tags
