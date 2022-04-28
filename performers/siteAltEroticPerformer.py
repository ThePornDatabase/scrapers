import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteAltEroticPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model_bio__top"]/span[@class="model_bio_heading"]/text()',
        'image': '//div[@class="cell_top model_picture"]/img/@src0_1x',
        'image_blob': True,
        'bio': '//div[contains(@class,"about-key")]/following-sibling::text()',
        'astrology': '//span[@class="extra-field__key" and contains(text(), "Sign")]/following-sibling::text()',
        'birthday': '//span[@class="extra-field__key" and contains(text(), "Age")]/following-sibling::text()',
        'ethnicity': '//span[@class="extra-field__key" and contains(text(), "Ethnicity")]/following-sibling::text()',
        'fakeboobs': '//span[@class="extra-field__key" and contains(text(), "Breasts")]/following-sibling::text()',
        'haircolor': '//span[@class="extra-field__key" and contains(text(), "Haircolor")]/following-sibling::text()',
        'height': '//span[@class="extra-field__key" and contains(text(), "Height")]/following-sibling::text()',
        'measurements': '//span[@class="extra-field__key" and contains(text(), "Measurements")]/following-sibling::text()',
        'piercings': '//span[@class="extra-field__key" and contains(text(), "Piercings")]/following-sibling::text()',
        'tattoos': '//span[@class="extra-field__key" and contains(text(), "Tattoos")]/following-sibling::text()',
        'pagination': '/tour/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'AltEroticPerformer'
    network = 'Alt Erotic'

    cookies = {'splash-page': '1'}

    start_urls = [
        'https://alterotic.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model-name"]/p/a/@href').getall()
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

    def get_height(self, response):
        height = super().get_height(response)
        height = height.lower()
        if "cm" in height and re.search(r'(\d{2,4}\s+?cm)', height):
            height = re.search(r'(\d{2,4}\s+?cm)', height).group(1)
            height = height.replace(" ", "")
        return height

    def get_fakeboobs(self, response):
        fakeboobs = super().get_fakeboobs(response)
        if "augmented" in fakeboobs.lower():
            return "Yes"
        return "No"
