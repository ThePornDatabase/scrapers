import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJoybearSpider(BaseSceneScraper):
    name = 'Joybear'
    network = 'Joybear'
    parent = 'Joybear'
    site = 'Joybear'

    start_urls = [
        'https://www.joybear.com',
    ]

    selector_map = {
        'title': '//div[@class="wide grey"]/div/span[@class="wide title"]/text()',
        'description': '//div[@class="wide grey"]/div/span[@class="wide text"]/text()',
        'date': '//span[@class="wide source"]/text()[contains(., "Published")]',
        're_date': r'(\d{1,2}\w{2}? \w+ \d{4})',
        'image': '//script[contains(text(), "poster")]/text()',
        're_image': r'poster.*?\"(.*?)\"',
        'performers': '//div[@class="wide grey"]/div/span[@class="wide cast"]/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '//script[contains(text(), "poster")]/text()',
        're_trailer': r'src:.*?//(.*?)\"',
        'external_id': r'movies/(.*)',
        'pagination': '/chapters/page-%s/?&sort=recent&tag=all',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class,"chapter")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
