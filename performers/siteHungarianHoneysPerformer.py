import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteHungarianHoneysPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//article[contains(@class,"bio-article")]/section/div[contains(@class,"container-default")]/div/h2/text()',
        'image': '//article[contains(@class,"bio-article")]/section/div[contains(@class,"container-default")]//img/@src0_2x',
        'image_blob': True,
        'bio': '//div[contains(@class, "rating-div")]/following-sibling::div[1]/p/text()',
        'gender': '',
        'astrology': '//strong[contains(text(), "Astrological")]/following-sibling::text()',
        'birthday': '//strong[contains(text(), "Date of")]/following-sibling::text()',
        'birthplace': '//strong[contains(text(), "Birthplace")]/following-sibling::text()',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '//strong[contains(text(), "Hair Color")]/following-sibling::text()',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        're_height': r'(\d+cm)',
        'measurements': '//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/models_%s_d.html?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'HungarianHoneysPerformer'
    network = 'Hungarian Honeys'

    start_urls = [
        'https://www.hungarianhoneys.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "item-model")]/div/a/@href').getall()
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

    def get_birthday(self, response):
        birthday = response.xpath('//strong[contains(text(), "Date of")]/following-sibling::text()')
        if birthday:
            birthday = birthday.get()
            birthday = self.parse_date(birthday, date_formats=['%d %B, %Y'])
            if birthday:
                return birthday.strftime('%Y-%m-%d')
        return None
