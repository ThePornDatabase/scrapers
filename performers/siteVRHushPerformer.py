import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteVRHushPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@id="model-name"]/text()',
        'image': '//div[@class="model-photo"]/img/@src',
        'bio': '//h1/following-sibling::p[1]/text()',
        'gender': '//span[contains(text(), "Gender")]/following-sibling::text()',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '//span[contains(text(), "Ethnicity")]/following-sibling::text()',
        'eyecolor': '//span[contains(text(), "Eye Color")]/following-sibling::text()',
        'fakeboobs': '',
        'haircolor': '//span[contains(text(), "Hair Color")]/following-sibling::text()',
        'height': '//span[contains(text(), "Height")]/following-sibling::text()',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//span[contains(text(), "Weight")]/following-sibling::text()',

        'pagination': '/models/sort/asc?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'VRHushPerformer'
    network = 'VR Hush'

    start_urls = [
        'https://vrhush.com',
    ]

    def get_gender(self, response):
        gender = super().get_gender(response)
        if gender:
            return gender
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="name-wrapper"]/h3/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_height(self, response):
        height = response.xpath('//span[contains(text(), "Height")]/following-sibling::text()')
        if height:
            height = height.get()
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'(\d+)\"', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None

    def get_weight(self, response):
        weight = response.xpath('//span[contains(text(), "Weight")]/following-sibling::text()')
        if weight:
            weight = weight.get()
            weight = re.search(r'(\d+)', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .453592)) + "kg"
                return weight
        return None
