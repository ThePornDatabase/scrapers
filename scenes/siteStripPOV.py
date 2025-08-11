import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStripPOVSpider(BaseSceneScraper):
    name = 'StripPOV'
    network = 'StripPOV'
    parent = 'StripPOV'
    site = 'StripPOV'

    start_urls = [
        'https://strippov.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2[contains(text(), "Categories")]/preceding-sibling::div[1]//text()',
        'date': '//meta[@property="og:image"]/@content',
        're_date': r'/(\d{4}-\w+-\d{1,2})/',
        'date_formats': ['%Y-%b-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h2/following-sibling::span/a[contains(@href, "/actor")]/text()',
        'tags': '//h2[contains(text(), "Categories")]/following-sibling::a[contains(@href, "/category")]/text()',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(\d+)-',
        'pagination': '/all/movie?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "co-12 col-md-6 mb-3")]')
        for scene in scenes:
            duration = scene.xpath('.//small[contains(@class, "duration")]/text()[contains(., ":")]')
            if duration:
                duration = duration.get()
                meta['duration'] = self.duration_to_seconds(re.sub(r'[^0-9:]+', '', duration))
            scene = scene.xpath('.//h3/ancestor::a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
