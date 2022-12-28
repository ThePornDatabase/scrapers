import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteDigitalVideoVisionPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@id="performer"]//h1/text()',
        'image': '//div[@class="performer-page"]//picture/img/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '//div[@id="performer"]//ul/li[contains(text(), "Ethnicity")]/text()',
        're_ethnicity': r'Ethnicity\: (.*)',
        'eyecolor': '//div[@id="performer"]//ul/li[contains(text(), "Eyes")]/text()',
        're_eyecolor': r'Eyes\: (.*)',
        'fakeboobs': '',
        'haircolor': '//div[@id="performer"]//ul/li[contains(text(), "Hair")]/text()',
        're_haircolor': r'Hair\: (.*)',
        'height': '//div[@id="performer"]//ul/li[contains(text(), "Height")]/text()',
        're_height': r'\: (.*)',
        'measurements': '//div[@id="performer"]//ul/li[contains(text(), "Meas")]/text()',
        're_measurements': r'(\d+\w+?-\d+-\d+)',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[@id="performer"]//ul/li[contains(text(), "Weight")]/text()',
        're_weight': r'(\d+)',

        'pagination': '/porn-stars.html?sort=ag_added&page=%s&hybridview=member',
        'external_id': r'model/(.*)/'
    }

    name = 'DigitalVideoVisionPerformer'
    network = 'Digital Video Vision'

    start_urls = [
        'https://digitalvideovision.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item"]/a[@class="performer"]/@href').getall()
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
        measurements = super().get_measurements(response)
        if measurements:
            return re.search(r'(\d{1,3}\w+)-', measurements).group(1).strip()
        return ''

    def get_weight(self, response):
        weight = super().get_weight(response)
        if weight:
            weight = str(round(int(weight) / 2.205)) + "kg"
            return weight
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            height = re.findall(r'(\d+)', height)
            inches = int(height[0]) * 12
            if len(height) > 1:
                inches = inches + int(height[1])
            height = str(round(inches * 2.54)) + "cm"
            return height
        return ''
