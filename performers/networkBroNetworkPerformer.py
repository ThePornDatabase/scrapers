import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkBroNetworkPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="model_picture"]/img/@src0_1x',
        'image_blob': True,
        'bio': '//p[@class="bio_description"]/text()',
        'gender': '',
        'astrology': '//span[@class="info_var" and contains(text(), "Sign")]/following-sibling::text()[1]',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//span[@class="info_var" and contains(text(), "Eye")]/following-sibling::text()[1]',
        'fakeboobs': '',
        'haircolor': '//span[@class="info_var" and contains(text(), "Hair")]/following-sibling::text()[1]',
        'height': '//span[@class="info_var" and contains(text(), "Height")]/following-sibling::text()[1]',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'BroNetworkPerformer'
    network = 'Bro Network'

    start_urls = [
        'https://thebronetwork.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_height(self, response):
        height = super().get_height(response)
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
