import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteFuckerMatePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="post-title"]/text()',
        'image': '//div[@id="post-thumbnail"]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="widget"]/p[1]/text()',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '//div[@class="widget"]//li[contains(text(), "Ethnicity")]/a[1]/text()',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '//div[@class="widget"]//li[contains(text(), "Ethnicity")]/a[2]/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/actor?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'FuckerMatePerformer'
    network = 'Fucker Mate'

    start_urls = [
        'https://www.fuckermate.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="post-thumbnail"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
