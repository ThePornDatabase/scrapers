import re
import scrapy
import string
from tpdb.BasePerformerScraper import BasePerformerScraper


class SkinzEroticaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"profile-details")]/h3[contains(text(), "About")]/text()',
        'image': '//img[contains(@class, "model_bio_thumb")]/@src0_2x',
        'image_blob': True,
        'cupsize': '//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        'measurements': '//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'pagination': '/tour/models/%s/latest/?g=',
        'external_id': r'model/(.*)/'
    }

    name = 'SkinzEroticaPerformer'
    network = 'SkinzErotica'

    start_urls = [
        'https://www.skinzerotica.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            if "https:" not in performer:
                performer = "https://www.skinzerotica.com/tour/" + performer
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.sub(r'[^0-9A-Z-]+', '', measurements.upper())
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                cupsize = re.sub(r'[^0-9A-Z-]+', '', cupsize.upper())
                cupsize = re.search(r'^(\d{2}\w+)', cupsize)
                if cupsize:
                    return cupsize.group(1)
        return ''

    def get_name(self, response):
        name = super().get_name(response)
        name = string.capwords(name.lower().replace("about", "").strip())
        return name

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            height = re.sub(r'[^0-9\'\"]+', '', height)
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'\d+?\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None
