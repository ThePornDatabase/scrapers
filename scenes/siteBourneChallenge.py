import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBourneChallengeSpider(BaseSceneScraper):
    name = 'BourneChallenge'
    network = 'Bourne Challenge'
    parent = 'Bourne Challenge'
    site = 'Bourne Challenge'

    start_urls = [
        'https://bournechallenge.com/movies/page/3/',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[contains(@class, "post__content")]/p/text()',
        'date': '//time/@datetime',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//ul[contains(@class, "talent__list")]/li/a/text()',
        'tags': '//ul[contains(@class, "tags__list")]/li/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/movies/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card-title"]/a/@href').getall()
        for scene in scenes:
            sceneid = re.search(r'(\d{4})/(\d{2})/(.*)/', scene)
            meta['id'] = f"{sceneid.group(1)}-{sceneid.group(2)}-{sceneid.group(3)}"
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
