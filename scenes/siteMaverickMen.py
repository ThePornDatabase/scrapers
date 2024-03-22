import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMaverickMenSpider(BaseSceneScraper):
    name = 'MaverickMen'
    network = 'Maverick Men'
    parent = 'Maverick Men'
    site = 'Maverick Men'

    start_urls = [
        'https://vod.maverickmen.com',
    ]

    selector_map = {
        'title': '//h1[@id="view_title"]/text()',
        'description': '//span[@id="view_description"]//text()',
        'date': '//strong[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="main_vid"]//img/@src',
        'external_id': r'.*=(.*?)$',
        'pagination': '/?page=videos&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="vid-list-thumb"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
