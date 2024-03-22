import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMaverickMenDirectsSpider(BaseSceneScraper):
    name = 'MaverickMenDirects'
    network = 'Maverick Men'
    parent = 'Maverick Men Directs'
    site = 'Maverick Men Directs'

    start_urls = [
        'https://vod.maverickmen.com',
    ]

    selector_map = {
        'title': '//div[@class="custom-container"]/div/div/h2/text()',
        'description': '//h5/following-sibling::p//text()',
        'date': '//i[contains(@class, "fa-clock")]/following-sibling::small/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//comment()[contains(., "img-responsive")]',
        're_image': r'(http.*?)[\'\"]',
        'external_id': r'.*/(.*?)$',
        'pagination': '/m/r/site/Maverick_Directs/ms/trailers?p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videobox2"]/figure/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title = title.lower().replace("teaser", "").strip()
        return string.capwords(title)
