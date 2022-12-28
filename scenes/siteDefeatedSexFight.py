import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Spider(BaseSceneScraper):
    name = 'DefeatedSexFight'
    network = 'Hentaied'
    parent = 'Defeated Sex Fight'
    site = 'Defeated Sex Fight'

    start_urls = [
        'https://defeatedsexfight.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"cont")]/p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"tagsmodels")]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'duration': '//div[@class="duration"]/text()',
        'trailer': '',
        'external_id': r'com/(.*)/',
        'pagination': '/all-videos/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
