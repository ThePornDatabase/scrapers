import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHotOlderMaleSpider(BaseSceneScraper):
    name = 'HotOlderMale'
    site = 'Hot Older Male'
    parent = 'Hot Older Male'
    network = 'Hot Older Male'

    start_urls = [
        'https://www.hotoldermale.com',
    ]

    selector_map = {
        'title': '//h2[@class="main_title"]/text()',
        'description': '//div[@class="p-5"]/p/text()',
        'date': '//h5[contains(text(), "Details:")]/text()[1]',
        're_date': r'(\w+ \d+, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@id="playerWrap"]/img/@src',
        'performers': '//span[@class="perfImage"]/a/text()',
        'tags': '//h5[contains(text(), "Categories")]/a/text()',
        'duration': '//h5[contains(text(), "Details:")]/text()[2]',
        'trailer': '',
        'external_id': r'/(\d+)-',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "scene_container")]/figure/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//h5[contains(text(), "Details:")]/text()[2]')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]', "", duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return ""
