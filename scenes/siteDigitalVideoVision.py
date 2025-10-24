import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDigitalVideoVisionSpider(BaseSceneScraper):
    name = 'DigitalVideoVision'
    network = 'Digital Video Vision'
    parent = 'Digital Video Vision'
    site = 'Digital Video Vision'

    cookies = [{"name": "ageConfirmed", "value": "true"}]

    start_urls = [
        'https://www.digitalvideovision.com',
    ]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//div[@class="synopsis"]/p/text()',
        'date': '//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]/a/img/@title',
        'tags': '//div[@class="tags"]/a/text()',
        'duration': '//div[@class="release-date"]/span[contains(text(), "Length")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/watch-newest-digital-videovision-clips-and-scenes.html?page=%s&hybridview=member',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="scene-preview-container"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            duration = re.search(r'(\d+) min', duration.get()).group(1)
            duration = str(int(duration) * 60)
            return duration
        return ''
