import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOopsFamilySpider(BaseSceneScraper):
    name = 'OopsFamily'
    network = 'OopsFamily'
    parent = 'OopsFamily'
    site = 'OopsFamily'

    start_urls = [
        'https://oopsfamily.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-detail__title")]/text()',
        'description': '//div[@class="hidden" and @data-id="description"]/text()',
        'date': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_date': r'(\d+ \w+, \d{4})',
        'date_formats': ['%d %B, %Y'],
        'image': '//script[contains(text(), "coreSettings")]/text()',
        're_image': r'poster[\'\"]:.*?[\'\"](.*?)[\'\"]',
        'performers': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/a/text()',
        'tags': '//div[contains(@class,"tags__container")]/a/text()',
        'duration': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_duration': r'(\d+:\d+)',
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
        image = response.xpath('//script[contains(text(), "coreSettings")]/text()').get()
        image = image.replace("\r", "").replace("\n", "").replace("\t", "")
        image = re.search(r'poster.*?(//.*?)[\'\"]', image).group(1)
        image = "https:" + image
        return image

