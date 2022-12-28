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
        'description': '//div[@class="exc"]/span/p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"tagsmodels")]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
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
