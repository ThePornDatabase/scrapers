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
        # The div.hidden[data-id=description] block is gone; og:description
        # carries the same synopsis.
        # 'description': '//meta[@property="og:description"]/@content',
        'date': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_date': r'(\d+ \w+, \d{4})',
        'date_formats': ['%d %B, %Y'],
        'image': '//script[contains(text(), "coreSettings")]/text()',
        're_image': r'poster[\'\"]:.*?[\'\"](.*?)[\'\"]',
        'performers': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/a/text()',
        # div.tags__container is gone and the site publishes no tag links at
        # all any more, so there is nothing left to read.
        'tags': '',
        'duration': '//div[@class="video-info mt-5"]/div[@class="video-info__text"]/div[@class="video-info__time"]/text()',
        're_duration': r'(\d+:\d+)',
        'external_id': r'.*/(.*?)$',
        'pagination': '/video?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//a[contains(@class, "video-card")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        # The poster used to be dug out of an inline coreSettings script. That
        # script is gone, so .get() returned None and every scene crashed on
        # None.replace -- the site is reachable again, which is why this only
        # surfaced now. og:image carries the same poster.
        image = response.xpath('//meta[@property="og:image"]/@content').get()
        if image:
            return image.strip()

        # Fall back to the inline poster reference if the meta tag ever goes.
        script = response.xpath('//script[contains(text(), "poster")]/text()').get()
        if script:
            match = re.search(r'poster[^\'\"]{0,12}[\'\"]?(https?:[^\'\" ,]+|//[^\'\" ,]+)', script.replace("\\/", "/"))
            if match:
                image = match.group(1)
                return image if image.startswith('http') else 'https:' + image
        return ''

