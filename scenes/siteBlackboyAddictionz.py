import re
import requests
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackboyAddictionzSpider(BaseSceneScraper):
    name = 'BlackboyAddictionz'
    network = 'Blackboy Addictionz'
    parent = 'Blackboy Addictionz'
    site = 'Blackboy Addictionz'

    start_urls = [
        'https://www.blackboyaddictionz.com',
    ]

    selector_map = {
        'title': '//h2[contains(@class, "sectionMainTitle")]/text()',
        'description': '//div[@class="p-5"]/p//text()',
        'date': '//h5[@class="strong" and contains(text(), "Details")]/text()[contains(., ",")]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@id="playerWrap"]/img/@src|//meta[@property="og:image"]/@content',
        'performers': '//div/span[@class="perfImage"]/a/text()',
        'tags': '//h5//a[contains(@href, "category") and not(contains(@href, "director"))]/text()',
        'external_id': r'',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//figure/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//h5[@class="strong" and contains(text(), "Details")]/text()[contains(., "min")]')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None
    
    def get_director(self, response):
        director = response.xpath('//h5//a[contains(@href, "category") and contains(@href, "director")]/text()')
        if director:
            director = director.get()
            director = re.search(r': (.*)', director)
            if director:
                return string.capwords(director.group(1))