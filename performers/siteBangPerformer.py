import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBangPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[contains(@class,"capitalize")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        're_image': r'(.*)\?',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '//div[contains(text(), "Born")]/span[1]/text()',
        're_birthday': r'(\w+ \d{1,2}, \d{4})',
        'birthplace': '//div[contains(./following-sibling::text(), "From")]/following-sibling::span[contains(@class, "bold")]/text()',
        'cupsize': '',
        'ethnicity': '//div[contains(text(), "Ethnicity")]/span[1]/text()',
        'eyecolor': '//text()[contains(., "Eye Color:")]/following-sibling::span[1]/text()',
        'fakeboobs': '',
        'haircolor': '//text()[contains(., "Hair Color:")]/following-sibling::span[1]/text()',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/pornstars?by=views.weekly&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BangPerformer'
    network = 'Bang'

    start_urls = [
        'https://www.bang.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "rounded-xl")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
