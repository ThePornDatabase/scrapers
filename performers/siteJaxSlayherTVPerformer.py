import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteJaxSlayherTVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title"]/text()',
        'image': '//div[@class="model_box"]/div/picture/source[1]/@srcset',
        'image_blob': True,
        'bio': '//div[@class="model_box"]//div[@class="description_top"]/div[@class="info"]/text()',
        'gender': '',
        'astrology': '',
        'birthday': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Birthdate")]/following-sibling::div/text()',
        'birthplace': '',
        'cupsize': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Measurements")]/following-sibling::div/text()',
        're_cupsize': r'(\d{2,3}\w+)?-',
        'ethnicity': '',
        'eyecolor': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Eyes")]/following-sibling::div/text()',
        'fakeboobs': '',
        'haircolor': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Hair")]/following-sibling::div/text()',
        'height': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Height")]/following-sibling::div/text()',
        'measurements': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Measurements")]/following-sibling::div/text()',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Weight")]/following-sibling::div/text()',

        'pagination': '/tour/models/a-z/page/%s',
        'external_id': r'model/(.*)/'
    }

    name = 'JaxSlayherTVPerformer'
    network = 'JaxSlayherTV'

    start_urls = [
        'https://jaxslayher.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item"]/a[@class="wrap_card"]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_weight(self, response):
        weight = response.xpath('//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Weight")]/following-sibling::div/text()')
        if weight:
            weight = weight.getall()
            weight = re.search(r'(\d+)', "".join(weight).strip())
            if weight:
                weight = weight.group(1)
                if weight:
                    return str(int(int(weight) * 0.45359237)) + "kg"
        return None

    def get_height(self, response):
        height = response.xpath('//div[@class="model_box"]//div[@class="description_main"]/ul/li/div[contains(text(), "Height")]/following-sibling::div/text()')
        if height:
            height = height.getall()
            height = "".join(height).strip()
            height = height.replace(" ", "")
            if "'" in height:
                height = re.sub(r'[^0-9\']', '', height)
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    feet = int(feet) * 12
                else:
                    feet = 0
                inches = re.search(r'\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                else:
                    inches = 0
                return str(int((feet + inches) * 2.54)) + "cm"
        return None
