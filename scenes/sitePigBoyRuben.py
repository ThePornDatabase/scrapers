import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePigBoyRubenSpider(BaseSceneScraper):
    name = 'PigboyRuben'
    site = 'Pigboy Ruben'
    parent = 'Pigboy Ruben'
    network = 'Pigboy Ruben'

    start_urls = [
        'https://pigboyruben.com',
    ]

    selector_map = {
        'title': '//div[@class="underTop"]/following-sibling::div[@class="header"][1]/h1[1]/text()',
        'description': '//div[@class="descr"]/text()',
        'date': '',
        'image': '//div[@class="clipifr"]/div/img/@src',
        'performers': '//div[@class="tagList"]/a[contains(@href, "model")]/div/text()',
        'tags': '//div[@class="tagList"]/div[not(@class="tagSeparator")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'id=(\d+)',
        'pagination': '/videos.php?leap=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="thumb"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Pigboy Ruben"
                perf['site'] = "Pigboy Ruben"
                performers_data.append(perf)
        return performers_data
