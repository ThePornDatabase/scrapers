import re
import dateparser
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class BabeArchivePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-details clear"]/h3[1]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'image_blob': True,
        'birthplace': '//li/strong[contains(text(),"Birthplace")]/following-sibling::text()',
        'measurements': '//li/strong[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//li/strong[contains(text(),"Height")]/following-sibling::text()',
        'weight': '//li/strong[contains(text(),"Weight")]/following-sibling::text()',
        'birthday': '//li/strong[contains(text(),"Birth")]/following-sibling::text()',
        'astrology': '//li/strong[contains(text(),"Sign:")]/following-sibling::text()',
        'pagination': '/models/%s/latest/?g=',
        'external_id': r'models/(.*)/'
    }

    name = 'BabeArchivePerformer'
    network = "Babe Archive"
    parent = "Babe Archive"

    start_urls = [
        'https://www.babearchives.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site': 'Babe Archive'}
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height:
                    height = re.search(r'(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ", "")
                return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight:
                    weight = re.search(r'(\d+\s?kg)', weight).group(1).strip()
                    weight = weight.replace(" ", "")
                return weight.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                image = "https://www.babearchives.com" + image
                return image.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace(" ", "").strip()
                measurements = re.search(r'(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    cupsize = re.search('(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.upper().strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace(" ", "").strip()
                measurements = re.search(r'(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    return measurements.upper().strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                return dateparser.parse(birthday.strip(), settings={'TIMEZONE': 'UTC'}).isoformat()
        return ''
