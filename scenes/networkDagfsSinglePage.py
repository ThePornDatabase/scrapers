import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkDaGFsSpider(BaseSceneScraper):
    name = 'DagfsSinglePage'
    network = 'dagfs'

    start_urls = [
        ['https://www.filf.com', 'FILF'],
        ['https://www.shedoesanal.com', 'She Does Anal'],
        ['https://www.steplesbians.com', 'Step Lesbians'],
    ]

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=link[0],
                                 callback=self.get_scenes,
                                 meta={'page': self.page, 'site': link[1], 'parent': link[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//p[@class="description"]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//img[@class="scene-img"]/@src',
        'performers': '//div[@class="name-ctn"]/span/text()',
        'tags': '',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="profile-inner"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        return self.parse_date('today').isoformat()
