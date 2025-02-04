import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGothGirlfriendsSpider(BaseSceneScraper):
    name = 'GothGirlfriends'
    site = 'Goth Girlfriends'
    parent = 'Goth Girlfriends'
    network = 'Goth Girlfriends'

    start_urls = [
        'https://www.gothgirlfriends.com'
    ]

    selector_map = {
        'title': '//div[@class="title"]/h1/text()',
        'description': '//p[@class="description"]/text()',
        'date': '//h2[contains(text(), "Release")]/following-sibling::p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="update_models"]/a/text()',
        'tags': '//div[@class="categories-holder"]/a/@title',
        'duration': '//h2[contains(text(), "Length")]/following-sibling::p/text()',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*)?\.htm',
        'pagination': '/categories/videos_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="thumb-pic"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
