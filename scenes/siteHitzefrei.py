import re
import scrapy
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper


class HitzefreiSpider(BaseSceneScraper):
    name = 'Hitzefrei'
    network = "Radical Entertainment"
    parent = "Hitzefrei"

    start_urls = [
        'https://tour.hitzefrei.com/'
    ]

    selector_map = {
        'title': '//div[contains(@class,"row-content-details")]/h1[@class="content-title"]/text()',
        'description': '//div[@class="content-description"]/p/text()',
        'date': '//p[@class="content-metas"]/span[@class="meta-value"][2]/text()',
        'image': '//div[@id="trailer-player"]/@data-screencap',
        'performers': '//div[@class="model-name"]/text()',
        'tags': '',
        'trailer': '//div[@id="trailer-player"]/@data-trailer',
        'external_id': r'/view/(\d*)/',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):

        scenes = response.xpath('//h1[@class="content-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).get()
        date.replace('Released:', '').replace('Added:', '').strip()
        return dateparser.parse(date.strip(), settings={'DATE_ORDER': 'DMY', 'TIMEZONE': 'UTC'}).isoformat()
