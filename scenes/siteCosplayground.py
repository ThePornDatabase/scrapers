import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCosplaygroundSpider(BaseSceneScraper):
    name = 'Cosplayground'
    network = 'Cosplayground'
    parent = 'Cosplayground'
    site = 'Cosplayground'

    start_urls = [
        'https://cosplayground.com',
    ]

    selector_map = {
        'title': '//div[@class="container"]//h2//text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::div/p//text()',
        'date': '',
        'image': '//video/@data-poster',
        'performers': '//span[contains(text(), "Models:")]/following-sibling::a/text()',
        'tags': '//h3[contains(text(), "Categories")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'.*s(\d+)',
        'pagination': '/parody-scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "row-cols")]/div[@class="col"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//script[contains(text(), "Tracker.track")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'duration".*?(\d+)', duration)
            if duration:
                return duration.group(1)
        return None
