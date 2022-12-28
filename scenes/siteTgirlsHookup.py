import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTgirlsHookupSpider(BaseSceneScraper):
    name = 'TgirlsHookup'
    network = 'Tgirls Hookup'
    parent = 'Tgirls Hookup'
    site = 'Tgirls Hookup'

    start_urls = [
        'https://www.tgirlshookup.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "toptitle_left")]/text()',
        'description': '//comment()[contains(., "setdesc")]/following-sibling::p/text()',
        'date': '//b[contains(text(), "Added")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[contains(@class, "player-thumb")]/img[contains(@id, "set-target")]/@src0_1x|//meta[@property="og:image"]/@content',
        'performers': '//div[@class="setdesc"]/a[contains(@href, "/models/")]/text()',
        'tags': '',
        'duration': '//div[contains(@class,"trailermovieruntime")]/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)\.htm',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "videoblock")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        return ['Trans']
