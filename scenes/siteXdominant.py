import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXDominantSpider(BaseSceneScraper):
    name = 'XDominant'
    network = 'XDominant Official'
    parent = 'XDominant Official'
    site = 'XDominant Official'

    start_urls = [
        'https://xdominant.com',
    ]

    selector_map = {
        'title': '//div[@class="video-full__name"]/text()',
        'description': '',
        'date': '//div[contains(@class,"flaticon-calendar")]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="video-full"]//video/@poster',
        'performers': '//div[@class="video-full__models"]/a/text()',
        'tags': '',
        'duration': '//div[contains(@class,"flaticon-clock")]/text()',
        'trailer': '//div[@class="video-full"]//video/source/@src',
        'external_id': r'/video/(\d+)/',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video__item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(map(lambda x: string.capwords(x.strip(" X")), performers))
        return performers

    def get_title(self, response):
        title = super().get_title(response)
        if " 4k" in title.lower():
            title = string.capwords(title.lower().replace(" 4k", ""))
        return title
