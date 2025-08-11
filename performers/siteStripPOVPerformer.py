import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class StripPOVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="row"]/div[1]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="row"]//h1/following-sibling::p[contains(@class, "mb-2")][1]//text()',
        'astrology': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Zodiac")]/span/text()',
        'birthday': '',
        'birthplace': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Hometown")]/span/text()',
        'cupsize': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Bra Size")]/span/text()',
        'ethnicity': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Ethnicity")]/span/text()',
        'eyecolor': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Eye Color")]/span/text()',
        'fakeboobs': '',
        'haircolor': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Hair Color")]/span/text()',
        'height': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Height")]/span/text()',
        'measurements': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Measurements")]/span/text()',
        'nationality': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Nationality")]/span/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[@class="row"]//h1/following-sibling::p[contains(text(), "Weight")]/span/text()',

        'pagination': '/actors?o=l&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'StripPOVPerformer'
    network = 'StripPOV'

    start_urls = [
        'https://strippov.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//img[contains(@class, "img-fluid")]/ancestor::a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            measurements = measurements.lower().replace("x", "-").strip()
            if measurements and re.search(r'(\d+[a-z]+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+[a-z]+-\d+-\d+)', measurements).group(1)
                return measurements.strip().upper()
            if measurements and re.search(r'(\d+)-(\d+)-(\d+)', measurements):
                measurements = re.search(r'(\d+)-(\d+)-(\d+)', measurements)
                cupsize = super().get_cupsize(response)
                if cupsize:
                    measurements = f"{cupsize}-{measurements.group(2)}-{measurements.group(3)}"
                else:
                    measurements = f"{measurements.group(1)}-{measurements.group(2)}-{measurements.group(3)}"
                return measurements.strip().upper()
        return ''

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.sub(r'[^0-9a-z]+', '', weight.lower())
        kilos = re.search(r'(\d+kg)', weight)
        if kilos:
            return kilos.group(1)
        pounds = re.search(r'^(\d+)', weight).group(1)
        pounds = str(int(int(pounds) * .4535)) + "kg"
        return pounds

    def get_height(self, response):
        height = super().get_height(response)
        height = re.sub(r'[^0-9a-z]+', '', height.lower())
        height = re.search(r'(\d+cm)', height)
        if height:
            return height.group(1)
