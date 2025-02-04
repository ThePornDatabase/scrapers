import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLeWoodSpider(BaseSceneScraper):
    name = 'LeWood'
    site = 'LeWood'
    parent = 'LeWood'
    network = 'LeWood'

    start_urls = [
        'https://www.lewood.com'
    ]

    cookies = [{"name": "ageConfirmed", "value": "true"}]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'date': '//span[contains(text(), "Released:")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//link[@rel="image_src"]/@href',
        'performers': '//div[@class="video-performer"]/a/img/following-sibling::span/span/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'type': 'Scene',
        'external_id': r'/(\d+)/',
        'pagination': '/newest-lewood-site-updates.html?page=%s&hybridview=member',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "scene-preview")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//span[contains(text(), "Length:")]/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
