import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheFemaleOrgasmSpider(BaseSceneScraper):
    name = 'TheFemaleOrgasm'
    network = 'The Female Orgasm'
    parent = 'The Female Orgasm'
    site = 'The Female Orgasm'

    start_urls = [
        'https://www.the-female-orgasm.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="player-window-play"]/following-sibling::img/@src0_2x',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[contains(text(), "Tags:")]/following-sibling::li/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*)\.htm',
        'pagination': '/explore/categories/Movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
