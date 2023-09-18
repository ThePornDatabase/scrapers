import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class MoviesTreasureIslandMediaSpider(BaseSceneScraper):
    name = 'TreasureIslandMediaMovies'
    network = 'Treasure Island Media'
    parent = 'Treasure Island Media'
    site = 'Treasure Island Media'

    start_urls = [
        'https://timstore.treasureislandmedia.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class,"ty-product-block-title")]//text()',
        'description': '//div[contains(@id,"content_description")]/div/p//text()',
        'date': '//span[@class="release-original-inner"]/text()',
        'date_formats': ['%B %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"row model-timremoteapis-wrap-row")]//a[contains(@class,"thumbnail-subtitle")]/text()',
        'tags': '',
        'duration': '//span[@class="run-time-inner"]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/movies/page-%s/?features_hash=1677_24-5855',
        'type': 'Movie',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="ty-grid-list__image"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title = title.lower()
        title = title.replace("(dvd)", "")
        title = string.capwords(title)
        return title

    def get_duration(self, response):
        duration = super().get_duration(response)
        duration = duration.lower()
        duration = duration.replace(" ", "")
        if "h" in duration and "m" in duration:
            hours = re.search(r'(\d+)h', duration).group(1)
            mins = re.search(r'(\d+)m', duration).group(1)
            duration = str(((int(hours) * 60) * 60) + (int(mins) * 60))
            return duration
        return None
