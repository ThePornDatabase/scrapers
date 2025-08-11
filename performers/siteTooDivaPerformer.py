import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteTooDivaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[contains(@class, "archive-title")]/text()',
        'image': '//img[contains(@class, "avatar-1000")]/@data-src',
        'image_blob': True,
        'bio': '//p[contains(@class, "archive-description")]/text()',
        'gender': '',
        'astrology': '',
        'birthday': '//p[contains(@class, "birthdate-value")]/text()',
        'birthplace': '//p[contains(@class, "birthplace-value")]/text()',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//p[contains(@class, "eyes-value")]/text()',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//p[contains(@class, "height-value")]/text()',
        'measurements': '//p[contains(@class, "measurements-value")]/text()',
        'nationality': '//p[contains(@class, "birthplace-value")]/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/divas/?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'TooDivaPerformer'
    network = 'TooDiva'

    start_urls = [
        'https://toodiva.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[@class="author"]/@href').getall()
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
