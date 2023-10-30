import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteMILFVRPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//script[contains(@type,"ld+json")]/text()',
        're_name': r'name[\'\"].*?[\'\"](.*?)[\'\"]',
        'image': '//div[@class="person__avatar"]/picture/img/@src',
        'image_blob': True,
        'bio': '//div[@class="person__content"]//text()',
        'gender': '//script[contains(@type,"ld+json")]/text()',
        're_gender': r'gender[\'\"].*?[\'\"](.*?)[\'\"]',
        'birthday': '//script[contains(@type,"ld+json")]/text()',
        're_birthday': r'birthDate[\'\"].*?[\'\"](.*?)[\'\"]',
        'height': '//script[contains(@type,"ld+json")]/text()',
        're_height': r'height[\'\"].*?[\'\"](.*?)[\'\"]',

        'pagination': '/milfs?p=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'MILFVRPerformer'
    network = 'MILFVR'

    start_urls = [
        'https://www.milfvr.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//li[@class="cards-list__item"]/div/a/@href').getall()
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
