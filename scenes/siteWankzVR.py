import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWankzVRSpider(BaseSceneScraper):
    name = 'WankzVR'
    network = 'Wankz'
    parent = 'Wankz VR'
    site = 'Wankz VR'

    start_urls = [
        'https://www.wankzvr.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "detail__body")]/div/h1/text()',
        'description': '//div[contains(@class, "detail__txt detail")]//text()',
        'date': '//span[contains(@class,"detail__date")]/text()',
        'date_formats': ['%d %B, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"detail__models") and contains(text(), "Starring:")]/a/text()',
        'tags': '//div[@class="tag-list__body"]//a/text()',
        'duration': '//script[contains(@type, "json")]/text()',
        're_duration': r'duration[\'\"]:[\'\"](PT.*?)[\'\"]',
        'trailer': '//script[contains(@type, "json")]/text()',
        're_trailer': r'contentUrl.*?[\'\"](http.*?)[\'\"]',
        'external_id': r'.*/(.*?)$',
        'pagination': '/?o=d&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class, "cards-list")]/div/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Virtual Reality")
        return tags

    def get_duration(self, response):
        duration = super().get_duration(response)
        if "PT" in duration or "M" in duration:
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
        return duration
