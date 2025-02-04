import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSubbyHubbySecondarySpider(BaseSceneScraper):
    name = 'SubbyHubbySecondary'
    network = 'Subby Hubby'
    parent = 'Subby Hubby'
    site = 'Subby Hubby'

    start_urls = [
        'https://www.subbyhubby.com',
    ]

    selector_map = {
        'title': '//span[@class="title_bar_hilite"]/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]//div[contains(@class,"update_date")]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//script[contains(text(), "thumbnail")]/text()',
        're_image': r'thumbnail.*?[\'\"](.*?)[\'\"]',
        'performers': '//span[@class="update_description"]/following-sibling::span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_description"]/following-sibling::span[@class="update_tags"]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*)_vids',
        'pagination': '/vod/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_date(self, response):
        scenedate = response.xpath('//div[@class="gallery_info"]//div[contains(@class,"update_date")]/text()')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = re.sub(r'[^0-9/]+', '', scenedate)
            scenedate = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
            return scenedate
        return None
