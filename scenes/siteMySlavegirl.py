import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMySlavegirlSpider(BaseSceneScraper):
    name = 'MySlavegirl'
    network = 'My Slavegirl'
    parent = 'My Slavegirl'
    site = 'My Slavegirl'

    start_urls = [
        'https://www.my-slavegirl.com',
    ]

    selector_map = {
        'title': '//h1[@class="h2"]/text()',
        'description': '//div[@class="custom_text"]/p/text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': r'collections/(.*)',
        'trailer': '//meta[@name="twitter:player:stream"]/@content',
        're_trailer': r'(.*\.mp4)',
        'pagination': '/collections/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "my-2")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
