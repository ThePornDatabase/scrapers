import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVlogXXXSpider(BaseSceneScraper):
    name = 'VlogXXX'
    network = 'VlogXXX'
    parent = 'VlogXXX'

    start_urls = [
        'https://vlogxxx.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@id="trailer-data"]/div/p/text()',
        'date': '//p[@class="date"]/text()',
        'image': '//div[@id="noMore"]/img/@src',
        'performers': '//h3[contains(text(),"pornstars")]/following-sibling::a/text()',
        'tags': '//h3[contains(text(),"Categories")]/following-sibling::a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"thumb-pic")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        externid = super().get_id(response)
        return externid.lower()
