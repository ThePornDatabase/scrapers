import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="head"]/p[1]/span/text()',
        'image': '//div[@class="content"]/div[1]/img/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/preview/guys?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'SpunkWorthyPerformer'
    network = 'SpunkWorthy'

    start_urls = [
        'https://spunkworthy.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="hs"]/p/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)


