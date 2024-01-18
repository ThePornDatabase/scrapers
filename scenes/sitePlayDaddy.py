import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePlayDaddySpider(BaseSceneScraper):
    name = 'PlayDaddy'
    network = 'PlayDaddy'
    parent = 'PlayDaddy'
    site = 'PlayDaddy'

    start_urls = [
        'https://www.playdaddy.com',
    ]

    selector_map = {
        'title': '//h2[@class="main_title"]/text()',
        'description': '//div[contains(@class, "container_styled_1")]/div[@class="p-5"]/p/text()',
        'date': '//div[contains(@class, "container_styled_1")]//i[@class="icon-clock-1"]/preceding-sibling::text()',
        're_date': r'(\w{3,4} \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="perfImage"]/a/text()',
        'tags': '//div[contains(@class, "container_styled_1")]//h5[contains(text(), "Categories")]/a/text()',
        'duration': '//div[contains(@class, "container_styled_1")]//i[@class="icon-clock-1"]/following-sibling::text()',
        're_duration': r'(\d+)',
        'trailer': '',
        'external_id': r'scene/(\d+)-',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="wrapperSceneTitle"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = super().get_duration(response)
        if duration:
            return str(int(duration) * 60)
        return None
