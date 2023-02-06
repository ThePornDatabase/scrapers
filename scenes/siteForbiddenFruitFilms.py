import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteForbiddenFruitsFilmsSpider(BaseSceneScraper):
    name = 'ForbiddenFruitsFilms'
    network = 'Forbidden Fruits Films'
    parent = 'Forbidden Fruits Films'
    site = 'Forbidden Fruits Films'

    start_urls = [
        'https://forbiddenfruitsfilms.com',
    ]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//h5[@class="tag-line"]/text()',
        'date': '//div[@class="release-date"]/span[contains(text(), "eleased:")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "video-performer-name")]/span/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/streaming-video-by-scene.html?page=%s&hybridview=member',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="release-date"]/span[contains(text(), "ength:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+) min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
