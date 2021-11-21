import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrandNewAmateursSpider(BaseSceneScraper):
    name = 'BrandNewAmateurs'
    network = 'Brand New Amateurs'
    parent = 'Brand New Amateurs'
    site = 'Brand New Amateurs'

    start_urls = [
        'https://www.brandnewamateurs.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a[contains(@href,"/categories/")]/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        're_trailer': r'video src=\"(.*\.mp4)\"',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]//a[not(contains(@href,"signup"))]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        externid = super().get_id(response)
        return externid.lower()
