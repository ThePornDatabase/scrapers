import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXtremelyTightSpider(BaseSceneScraper):
    name = 'XtremelyTight'
    network = 'Xtremely Tight'
    parent = 'Xtremely Tight'
    site = 'Xtremely Tight'

    start_urls = [
        'https://www.xtremely-tight.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "details")]/div/p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "models")]//a/text()',
        'tags': '//span[contains(@title, "Categories")]//a/text()',
        'duration': '//span[contains(@class, "fa5-text") and contains(text(), "minutes")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': r'.*/(.*?)$',
        'pagination': '/collections/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        image = super().get_image(response)
        sceneid = re.search(r'collections/(.*?)/', image).group(1)
        return sceneid

    def get_date(self, response):
        sceneyear = response.xpath(r'//span[contains(@title, "roduction year")]/span/text()')
        if sceneyear:
            sceneyear = sceneyear.get()
            sceneyear = re.search(r'(\d{4})', sceneyear)
            if sceneyear:
                return sceneyear.group(1) + "-01-01"
        return None
