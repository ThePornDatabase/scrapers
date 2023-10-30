import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkCherryPimpsPerformerSpider(BasePerformerScraper):
    name = 'CherryPimpsPerformer'
    network = 'Cherry Pimps'

    selector_map = {
        'name': '//h2/span[1]/text()',
        'image': '//div[contains(@class, "model-picture")]/img/@src0_3x|//div[contains(@class, "model-picture")]/img/@src0_2x|//div[contains(@class, "model-picture")]/img/@src0_1x',
        'image_blob': True,
        'astrology': '//div[@class="model-stats"]//strong[contains(text(), "Astrological")]/following-sibling::text()',
        'birthday': '//div[@class="model-stats"]//strong[contains(text(), "Date of Birth")]/following-sibling::text()',
        'birthplace': '//div[@class="model-stats"]//strong[contains(text(), "Birthplace")]/following-sibling::text()',
        'cupsize': '',
        'ethnicity': '//div[@class="model-stats"]//strong[contains(text(), "Race")]/following-sibling::text()',
        'eyecolor': '//div[@class="model-stats"]//strong[contains(text(), "Eye")]/following-sibling::text()',
        'fakeboobs': '',
        'haircolor': '//div[@class="model-stats"]//strong[contains(text(), "Hair")]/following-sibling::text()',
        'height': '//div[@class="model-stats"]//strong[contains(text(), "Height")]/following-sibling::text()',
        're_height': r'(\d+\s?cm)',
        'measurements': '//div[@class="model-stats"]//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'nationality': '//div[@class="model-stats"]//strong[contains(text(), "Ethnicity")]/following-sibling::text()',
        'piercings': '//div[@class="model-stats"]//strong[contains(text(), "Piercings")]/following-sibling::text()',
        'tattoos': '//div[@class="model-stats"]//strong[contains(text(), "Tattoos")]/following-sibling::text()',
        'weight': '//div[@class="model-stats"]//strong[contains(text(), "Weight")]/following-sibling::text()',
        're_weight': r'(\d+\s?kg)',

        'pagination': '/models//models_%s.html?g=f',
        'external_id': r'model/(.*)/'
    }

    start_urls = [
        'https://cherrypimps.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-thumb"]/a[contains(@href, "model")]/@href').getall()
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
        try:
            if 'birthday' in self.selector_map:
                birthday = self.cleanup_text(self.get_element(response, 'birthday', 're_birthday'))
                if birthday:
                    return self.parse_date(birthday).strftime('%Y-%m-%d')
        except:
            return ''
        return ''
