import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAltEroticSpider(BaseSceneScraper):
    name = 'AltErotic'
    network = 'Alt Erotic'
    parent = 'Alt Erotic'
    site = 'Alt Erotic'

    start_urls = [
        'https://alterotic.com',
    ]

    cookies = {'splash-page': '1'}

    selector_map = {
        'title': '//div[@class="breadcrumbs-tour"]/following-sibling::div[1]/div[@class="title-category"]/h3/text()',
        'description': '//div[@class="titleBlock" and .//h3[contains(text(), "VIDEO DESCRIPTION")]]/following-sibling::div[@class="trailer-details"]/span/text()',
        'date': '//div[@class="trailer-details"]/span[contains(text(), "Released")]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="Vcontainer"]//img/@src0_1x',
        'performers': '//div[@class="trailer-details"]/span[contains(text(), "Featuring")]/a/text()',
        'tags': '//div[@class="trailer-details"]//span[contains(text(), "Categories")]/a/text()',
        'trailer': '//div[@class="Vcontainer"]/a/@onclick',
        're_trailer': r'(http.*?\.mp4)',
        'external_id': r'updates/(.*?)\.html',
        'pagination': '/tour/videos/page_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateThumbnail"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies, headers=self.headers)

    def get_id(self, response):
        sceneid = self.get_element(response, 'image')
        if sceneid:
            idsearch = re.search(r'.*?\/\/.*?\/.*?\/.*?\/.*?\/.*?\/(.*?)_', sceneid)
            if idsearch:
                idsearch = idsearch.group(1)
                if re.search(r'(\d{3,6})', idsearch):
                    return idsearch.strip()
        return super().get_id(response)
