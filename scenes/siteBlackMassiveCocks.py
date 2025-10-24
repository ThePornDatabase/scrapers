import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackMassiveCocksSpider(BaseSceneScraper):
    name = 'BlackMassiveCocks'
    network = 'West Coast Productions'
    parent = 'Black Massive Cocks'
    site = 'Black Massive Cocks'

    start_urls = [
        'https://blackmassivecocks.com',
    ]

    cookies = [{"name": "ageConfirmed", "value": True}]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '',
        'date': '//span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//link[@rel="image_src"]/@href|//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"video-performer-container")]//a//text()',
        'tags': '//div[@class="tags"]/a/text()',
        'duration': '//span[contains(text(), "Length")]/following-sibling::text()',
        're_duration': r'(\d+) min',
        'trailer': '',
        'external_id': r'/(\d+)/',
        # ~ 'pagination': '/watch-newest-black-massive-cocks-clips-and-scenes.html?page=%s&hybridview=member',
        'pagination': '/black-massive-cocks-scenes.html?page=%s&hybridview=member',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"scene-preview")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//span[contains(text(), "Length")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+) min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
