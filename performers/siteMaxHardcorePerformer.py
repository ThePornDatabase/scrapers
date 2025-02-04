import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteMaxHardcorePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Name")]/following-sibling::div[1]/text()',
        'image': '//div[@class="profile__thumb"]/img/@src',
        'image_blob': True,
        'birthday': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Dob")]/following-sibling::div[1]/text()',
        'ethnicity': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Ethnicity")]/following-sibling::div[1]/text()',
        'eyecolor': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Eyes")]/following-sibling::div[1]/text()',
        'haircolor': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Hair")]/following-sibling::div[1]/text()',
        'height': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Height")]/following-sibling::div[1]/text()',
        'measurements': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Measurements")]/following-sibling::div[1]/text()',
        'weight': '//div[@class="pdesc col"]//div[contains(@class, "label") and contains(text(), "Weight")]/following-sibling::div[1]/text()',

        'pagination': '/models/page%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'MaxHardcorePerformer'
    network = 'Max Hardcore'

    start_urls = [
        'https://www.max-hardcore.com',
    ]

    def clean_field(self, field):
        field2 = re.sub(r'[^a-z]+', '', field.lower())
        if field2 == "na":
            return ""
        else:
            return field

    def get_gender(self, response):
        performer = self.get_name(response)
        if "Max Hardcore" in performer:
            return "Male"
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="mitem__inner"]/a[contains(@href, "models")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            measurements = self.clean_field(measurements)
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
                measurements = self.clean_field(measurements)
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        height = self.clean_field(height)
        if "-" in height:
            height = re.sub(r'[^0-9-]', '', height)
            feet = re.search(r'(\d+)-', height)
            if feet:
                feet = feet.group(1)
                feet = int(feet) * 12
            else:
                feet = 0
            inches = re.search(r'-(\d+)', height)
            if inches:
                inches = inches.group(1)
                inches = int(inches)
            else:
                inches = 0
            return str(int((feet + inches) * 2.54)) + "cm"
        return None

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = self.clean_field(weight)
        if weight:
            weight = re.search(r'(\d+)', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .453592)) + "kg"
                return weight
        return None

    def get_birthday(self, response):
        birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
        birthday = self.clean_field(birthday)
        return birthday

    def get_haircolor(self, response):
        return self.clean_field(super().get_haircolor(response))

    def get_eyecolor(self, response):
        return self.clean_field(super().get_eyecolor(response))

    def get_ethnicity(self, response):
        return self.clean_field(super().get_ethnicity(response))
