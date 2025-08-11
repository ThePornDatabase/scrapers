import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTooDivaSpider(BaseSceneScraper):
    name = 'TooDiva'
    network = 'TooDiva'
    parent = 'TooDiva'
    site = 'TooDiva'

    start_urls = [
        'https://toodiva.com',
    ]

    selector_map = {
        'title': '//h1[contains(@itemprop, "headline")]/text()',
        'description': '//div[@itemprop="articleBody"]/p/text()',
        'date': '//head/meta[@property="article:published_time"][1]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//head/meta[@property="og:image"][1]/@content',
        'performers': '//h2[contains(@class, "author-title")]/a/span/text()',
        'tags': '',
        'duration': '//article[contains(@id, "post")]/div[1]//span[contains(@class, "duration")]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/members/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//header/following-sibling::div[1]/div/div[@id="primary"]/div[1]/div[1]/ul[1]/li/article/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
