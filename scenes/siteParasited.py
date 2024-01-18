import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteParasitedSpider(BaseSceneScraper):
    name = 'Parasited'
    network = 'Hentaied'
    parent = 'Parasited'
    site = 'Parasited'

    start_urls = [
        'https://parasited.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@id="fullstory"]/p/span/text()[not(contains(., "Read Less"))]',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//img[contains(@alt, "model icon")]/following-sibling::div[@class="taglist"]/a/text()',
        'director': '//img[contains(@alt, "director icon")]/following-sibling::span/a/text()',
        'tags': '//ul[contains(@class,"post-categories")]/li/a/text()',
        'duration': '//div[@class="duration"]/text()',
        'trailer': '//video[@id="singlepreview"]/@src',
        'external_id': r'com/(.*)/',
        'pagination': '/all-videos/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="duration"]/text()')
        if duration:
            duration = duration.getall()
            duration = "".join(duration)
            duration = duration.strip()
            if ":" in duration:
                return self.duration_to_seconds(duration)
        return None
