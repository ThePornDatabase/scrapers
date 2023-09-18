import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOnlyTartsSpider(BaseSceneScraper):
    name = 'OnlyTarts'
    network = 'OnlyTarts'
    parent = 'OnlyTarts'
    site = 'OnlyTarts'

    start_urls = [
        'https://onlytarts.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-detail__title")]/text()',
        'description': '//div[@class="hidden" and @data-id="description"]/text()',
        'date': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_date': r'(\d+ \w+, \d{4})',
        'date_formats': ['%d %B, %Y'],
        'image': '//script[contains(text(), "window.initials")]/text()',
        're_image': r'poster.*?(http.*?)[\'\"]',
        'performers': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/a/text()',
        'tags': '//div[contains(@class,"tags__container")]/a/text()',
        'duration': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_duration': r'(\d+:\d+)',
        'trailer': '//script[contains(text(), "window.initials")]/text()',
        're_trailer': r'.*url.*?(http.*?1080p.*?)[\'\"].*',
        'external_id': r'.*/(.*?)$',
        'pagination': '/video?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class, "video-card")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        return image.replace('\\/', '/')

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        return trailer.replace('\\/', '/')
