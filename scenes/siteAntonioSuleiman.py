import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAntonioSuleimanSpider(BaseSceneScraper):
    name = 'AntonioSuleiman'
    network = 'Antonio Suleiman'
    parent = 'Antonio Suleiman'
    site = 'Antonio Suleiman'

    start_urls = [
        'https://antoniosuleiman.com',
    ]

    cookies = [{"name": "lang", "value": "0"}, {"name": "warn", "value": "true"}]

    selector_map = {
        'title': '//div[contains(@class, "updatesBlock")]/div[contains(@class, "section-heading")]/h3/text()',
        'description': '//div[contains(@class,"updatesBlock")]/div[@class="wrapper"]/p/span[contains(@class,"tour_update_models")]/../following-sibling::div[1]/text()',
        'date': '//div[contains(@class, "updateDetails")]//p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"updatesBlock")]/div[@class="wrapper"]/p/span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'updates/(.*)\.htm',
        'pagination': '/categories/updates_%s_d.html?lang=0',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href, "/updates/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
