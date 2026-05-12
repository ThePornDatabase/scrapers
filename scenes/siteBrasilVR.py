import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrasilVRSpider(BaseSceneScraper):
    name = 'BrasilVR'
    network = 'BrasilVR'
    parent = 'BrasilVR'
    site = 'BrasilVR'

    start_urls = [
        'https://www.brasilvr.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[contains(@class, "detail__txt")]//text()',
        'date': '//span[@class="detail__date"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "detail__content")]//div[contains(@class, "detail__models")]/a/text()',
        'tags': '//div[contains(@class, "tag-list") and contains(@class, "body")]//a/text()',
        'external_id': r'.*-(\d+)',
        'pagination': '/?o=d&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card__body"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//span[@class="time"]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "BrasilVR"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)
        return performers_data
    