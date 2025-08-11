import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "title-inner")]/h2/text()',
        'image': '//div[contains(@class, "avatar")]/div[@class="image"]/img/@src',
        'image_blob': True,
        'bio': '//span[contains(text(), "Biography")]/following-sibling::span[1]/text()',
        'birthday': '//span[contains(text(), "Dob")]/following-sibling::span[1]/text()',
        'cupsize': '//span[contains(text(), "Measurements")]/following-sibling::span[1]/text()',
        'eyecolor': '//span[contains(text(), "Eyes")]/following-sibling::span[1]/text()',
        'haircolor': '//span[contains(text(), "Hair")]/following-sibling::span[1]/text()',
        'height': '//span[contains(text(), "Height")]/following-sibling::span[1]/text()',
        'weight': '//span[contains(text(), "Weight")]/following-sibling::span[1]/text()',

        'pagination': '/models/rating/page%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'VRLatinaPerformer'
    network = 'VRLatina'

    start_urls = [
        'https://vrlatina.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "item-col")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            height = re.search(r'(\d+)', height)
            if height:
                return height.group(1) + "cm"

    def get_weight(self, response):
        weight = super().get_weight(response)
        if weight:
            weight = re.search(r'(\d+)', weight)
            if weight:
                return weight.group(1) + "kg"

    def get_ethnicity(self, response):
        return "Latin"
