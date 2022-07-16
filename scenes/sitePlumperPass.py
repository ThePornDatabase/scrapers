import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePlumperPassSpider(BaseSceneScraper):
    name = 'PlumperPass'
    network = 'Plumper Pass'
    parent = 'Plumper Pass'
    site = 'PlumperPass'

    start_urls = [
        'https://www.plumperpass.com',
    ]

    cookies = {
        'ppWarningPassed': '1',
        'tlimit': '1'
    }

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    selector_map = {
        'title': '//div[contains(@class, "vidinfo")]/h2/text()',
        'description': '//div[contains(@class, "vidinfo")]/p//text()',
        'date': '//div[@class="titlerow2"]//h3[@class="releases"]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "playlist")]/text()',
        're_image': r'(faceimages.*\.jpg)',
        'performers': '//div[@class="titlerow2"]//h3[@class="releases"]/a/text()',
        'tags': '//div[@class="titlerow2"]//h2/following-sibling::p/a/text()',
        'trailer': '',
        'external_id': r'lid=(\d+)',
        'pagination': '/t1/show.php?a=584_%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "vidblock")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                scene = "https://www.plumperpass.com/t1/" + scene
                meta['id'] = re.search(self.get_selector_map('external_id'), scene).group(1).strip()
                yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = self.get_element(response, 'image', 're_image')
            return "https://www.plumperpass.com/t1/" + image.replace(' ', '%20')
        return ''
