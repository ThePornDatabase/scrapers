import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDeviantAssSpider(BaseSceneScraper):
    name = 'DeviantAss'
    network = 'Deviant Ass'
    parent = 'Deviant Ass'
    site = 'Deviant Ass'

    start_urls = [
        'https://deviantass.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "updatesBlock")]/div[contains(@class, "section-heading")]/h3/text()',
        'description': '//div[@class="wrapper"]//span[contains(@class,"tour_update_models")]/../following-sibling::div/text()',
        'date': '//div[@class="updateDetails"]/div[1]/div[1]/p[1]/text()',
        'image': '//meta[@property="og:image"]/@content|//meta[@property="twitter:image"]/@content',
        'performers': '//div[@class="wrapper"]//span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*)?\.html',
        'pagination': '/categories/movies_%s_d.html?lang=0'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, "/updates/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
