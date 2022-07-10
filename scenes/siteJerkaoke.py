import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJerkaokeSpider(BaseSceneScraper):
    name = 'Jerkaoke'
    network = 'Jerkaoke'
    parent = 'Jerkaoke'
    site = 'Jerkaoke'

    start_urls = [
        'https://www.jerkaoke.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//main[@id="MusContainer"]//p[contains(@class, "fw-lighter")]/text()',
        'date': '//div[contains(text(), "Released")]/following-sibling::div/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//main[@id="MusContainer"]/div/div/img/@src',
        'performers': '//div[contains(text(), "Cast")]/following-sibling::div/a/text()',
        'tags': '//main[@id="MusContainer"]//a[contains(@href, "tags")]/span/text()',
        'trailer': '',
        'external_id': r'trailers/(.*?)\?',
        'pagination': '/videos?sort=published_at&page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "mb-3")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
