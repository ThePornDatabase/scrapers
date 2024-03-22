import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEnjoyxSpider(BaseSceneScraper):
    name = 'Enjoyx'
    site = 'Enjoyx'
    parent = 'Enjoyx'
    network = 'Enjoyx'

    start_urls = [
        'https://enjoyx.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "video-detail__title")]/text()',
        'description': '',
        'date': '//div[contains(@class,"desktop-sidebar")]//div[contains(@class, "video-info__time")]/text()',
        're_date': r'(\d{1,2} \w+, \d{4})',
        'date_formats': ['%d %B, %Y'],
        'image': '//script[contains(text(), "poster") and contains(text(), "coreSettings")]/text()',
        're_image': r'poster.*?url.*?(http.*?)[\'\"]',
        'performers': '//div[contains(@class,"desktop-sidebar")]//div[@class="video-info__text"]/a/text()',
        'tags': '//div[contains(@class, "tags__container")]/a/text()',
        'duration': '//div[contains(@class,"desktop-sidebar")]//div[contains(@class, "video-info__time")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/video?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class, "videos-item")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//script[contains(text(), "poster") and contains(text(), "coreSettings")]/text()')
        if image:
            image = "".join(image.get()).replace("\r", "").replace("\n", "").replace("\t", "")
            image = re.search(r'poster.*?url.*?(http.*?)[\'\"]', image)
            if image:
                return image.group(1)
        return ""
