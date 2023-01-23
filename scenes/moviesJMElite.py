import re
import string
from datetime import datetime
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class LjacquieetmicheleliteMovieSpider(BaseSceneScraper):
    name = 'JEMovie'

    start_urls = [
    'https://www.jacquieetmichelelite.com'
]

    selector_map = {
        'title': '//h1[contains(@class,"video-detail__title")]/text()',
        'description': '//div[contains(@class,"video-detail__description")]/text()',
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'duration': '//script[contains(@type, "json")]/text()',
        're_duration': r'duration.*?T(.*?)\"',
        'image': '//img[contains(@class,"video-detail__poster__img")]/text()',
        'performers': '//p[contains(@class,"actor-item__title")]/text()',
        'tags': '',
        'studio': '//li[@class="video-detail__info"]/a/text()',
        'director': '//ul[@class="video-detail__infos"]/li[3]/text()',
        'external_id': r'elite/(\d+)/',
        'pagination': '/en/porn-movies-p-%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//a[@class="video-item"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene )
