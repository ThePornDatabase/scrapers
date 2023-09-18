import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class SinematicaSpider(BaseSceneScraper):
    name = 'Sinematica'
    network = 'Sinematica'
    parent = 'Sinematica'

    start_urls = [
        'https://www.sinematica.com/'
    ]

    selector_map = {
        'title': '//div[contains(@class, "video-title")]/h1[@class="description"]/text()',
        'description': '//div[@class="synopsis"]//text()',
        'date': '//span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'duration': '//span[contains(text(), "Length")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "video-details-container")]//span[contains(@class, "video-performer-name")]/span/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': r'/(\d+)/',
        'trailer': '',
        'pagination': '/watch-newest-sinematica-clips-and-scenes.html?page=%s&hybridview=member'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="scene-preview-container"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            scenelength = 0
            duration = duration.get()
            if "min" in duration:
                duration = re.search(r'(\d+) min', duration)
                if duration:
                    minutes = duration.group(1)
                    scenelength = scenelength + (int(minutes) * 60)
            return str(scenelength)
        return ""
