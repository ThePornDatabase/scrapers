import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="model-name"]/text()',
        'image': '//div[@class="model-thumbnail"]/img/@src',
        'image_blob': True,
        'astrology': '//b[contains(text(), "Astrological")]/following-sibling::text()',
        'birthday': '//b[contains(text(), "Age:")]/following-sibling::text()',
        're_birthday': r'(\w+ \d{1,2}, \d{4})',
        'measurements': '//b[contains(text(), "Measurements:")]/following-sibling::text()',

        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'GothGirlfriendsPerformer'
    network = 'Goth Girlfriends'

    start_urls = [
        'https://www.gothgirlfriends.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="pornstar-pic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            return cupsize.strip()
        else:
            if 'measurements' in self.selector_map:
                measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''

    def get_height(self, response):
        height = response.xpath('//b[contains(text(), "Height:")]/following-sibling::text()')
        if height:
            height = height.get()
            height = re.sub(r'[^a-z0-9]+', '', height)
            height = re.search(r'(\d+)cm', height)
            if height:
                return height.group(1)
        return None
