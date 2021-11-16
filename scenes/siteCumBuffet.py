import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCumBuffetSpider(BaseSceneScraper):
    name = 'CumBuffet'
    network = 'Cum Buffet'
    parent = 'Cum Buffet'
    site = 'Cum Buffet'

    start_urls = [
        'https://www.cumbuffet.com',
    ]

    selector_map = {
        'title': '//div[@class="content"]/div/h2/text()',
        'description': '',
        'date': '',
        'image': '//div[@class="vp"]/div[contains(@class,"player")]/@style',
        're_image': r'(http.*\.jpg)',
        'performers': '//div[contains(@class,"tags")]/a[contains(@href,"/girl/")]/text()',
        'tags': '//div[contains(@class,"tags")]/ul/li/a/text()',
        'external_id': r'sample/(.*?)/',
        'trailer': '//video/source/@src',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def start_requests(self):
        yield scrapy.Request(url="https://www.cumbuffet.com/samples",
                             callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video"]')
        for scene in scenes:
            date = scene.xpath('.//div[@class="date"]/text()').get()
            if date:
                meta['date'] = self.parse_date(date.strip(), date_formats=['%b %d, %Y']).isoformat()
            else:
                meta['date'] = self.parse_date('today').isoformat()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
