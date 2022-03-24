import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTenshigaoSpider(BaseSceneScraper):
    name = 'Tenshigao'
    network = 'Tenshigao'
    parent = 'Tenshigao'
    site = 'Tenshigao'

    start_urls = [
        'https://tenshigao.com',
    ]

    selector_map = {
        'title': '//title/text()',
        're_title': r'(.*) ?|',
        'description': '//div[@class="videoinfo"]/h1/text()',
        'date': '//div[@class="video-date"]/text()',
        'image': '//video/@poster',
        'image_blob': True,
        'performers': '//div[@class="model-thumb"]//h5/a/text()',
        'tags': '//div[@class="cat"]/a/text()',
        'external_id': r'\.com/(\d+)/',
        'trailer': '',  # Available but blocked for non-scraper
        'pagination': '/japanese-porn/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb"]/a[@class="block"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        if page == 1:
            return "https://tenshigao.com/japanese-porn/"
        return self.format_url(base, self.get_selector_map('pagination') % page)
