import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLezCrushSpider(BaseSceneScraper):
    name = 'LezCrush'
    network = 'Lez Crush'
    parent = 'Lez Crush'
    site = 'Lez Crush'

    start_urls = [
        'https://lezcrush.com',
    ]

    cookies = {'accepted': '1', 'ex_referrer': 'https%3A%2F%2Flezcrush.com%2Ftour%2Fpages.php%3Fid%3Denter'}

    selector_map = {
        'title': '//span[@class="updateTitle"]/text()',
        'description': '',
        'date': '//span[@class="updateDate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="firstPic"]/a/img/@src0_2x',
        'performers': '//object/a[contains(@href, "/models/")]/text()',
        'tags': '//span[@class="updateTags"]/a/text()',
        'trailer': '//div[@class="firstPic"]/a/@onclick',
        're_trailer': r'tload\(\'(.*\.mp4)',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
