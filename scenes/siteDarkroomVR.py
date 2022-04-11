import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDarkroomVRSpider(BaseSceneScraper):
    name = 'DarkroomVR'
    network = 'POVR'
    parent = 'DarkroomVR'
    site = 'DarkroomVR'

    start_urls = [
        'https://darkroomvr.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-detail__title")]/text()',
        'description': '//div[@class="video-detail__description mt-5"]/div[2]/text()',
        'date': '//div[contains(@class,"hide-sm-min")]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_date': r'(\d{1,2} \w+, \d{4})',
        'date_formats': ['%d %B, %Y'],
        'image': '//div[contains(@class,"video-detail__image-container")]/img/@src',
        're_image': r'(.*\.jpg)',
        'image_blob': True,
        'performers': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/a/text()',
        'tags': '//div[@class="tags__container"]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/video?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="video-card__item"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = list(map(lambda x: x.strip().lower(), performers.getall()))

        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                tags = list(map(lambda x: x.strip().lower(), tags.getall()))

            tags2 = tags.copy()
            for tag in tags2:
                matches = ['5k', '6k', '7k']
                if any(x in tag.lower() for x in matches):
                    tags.remove(tag)

            tags = list(map(lambda x: x.strip().title(), tags))
            return tags
        return []
