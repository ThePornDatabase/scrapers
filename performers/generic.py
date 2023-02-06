import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
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

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = ''
    network = ''

    start_urls = [
        '',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'\d+.*?-.*?\d+.*?-.*?\d+', measurements):
                measurements = measurements.replace("B", "").replace("W", "").replace("H", "")
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                if 'measurements' in self.selector_map:
                    measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                    if measurements and re.match(r'\d+.*?-.*?\d+.*?-.*?\d+', measurements):
                        breasts = re.search(r'(\d+).*?-.*?\d+.*?-.*?\d+', measurements).group(1)
                        cupsize = breasts.strip() + cupsize.strip()
                        if cupsize:
                            return cupsize.strip()
                return cupsize.strip()
        return ''
