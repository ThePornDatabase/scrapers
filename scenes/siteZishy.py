import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteZishySpider(BaseSceneScraper):
    name = 'Zishy'
    network = 'Zishy'
    parent = 'Zishy'
    site = 'Zishy'

    start_urls = [
        'https://www.zishy.com',
    ]

    selector_map = {
        'title': '//div[@id="albumhead"]/div/span[1]/text()',
        'description': '//div[@id="descrip"]/text()',
        'date': '//div[@id="albumhead"]/div/span[2]/text()',
        're_date': r'(\w+ \d{2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[contains(@id, "media-player")]/a/img/@style',
        're_image': r'url\((.*?)\)',
        'performers': '//span[@class="moreof"]/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/?q=with_videos&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="albumcover"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(map(lambda x: string.capwords(x.replace("#", "").strip()), performers))
        return performers
