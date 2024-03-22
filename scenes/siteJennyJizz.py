import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJennyJizzSpider(BaseSceneScraper):
    name = 'JennyJizz'
    site = 'Jenny Jizz'
    parent = 'Jenny Jizz'
    network = 'Jenny Jizz'

    start_urls = [
        'https://www.jennyjizz.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "pagetitle")]//h1/text()',
        'description': '//div[@class="videocontent"]/p/text()',
        'date': '//div[@class="videodetails"]/p[@class="date"]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="videoplayer"]/img/@src0_3x|//div[@class="videoplayer"]/img/@src0_2x|//div[@class="videoplayer"]/img/@src0_1x',
        'performers': '//span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '',
        'duration': '//div[@class="videodetails"]/p[@class="date"]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/Movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h3/a[contains(@href, "/trailers/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        return super().get_id(response).lower()
