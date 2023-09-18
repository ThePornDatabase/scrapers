import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteTimeTalesPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "numbers-top")]/h1/text()',
        'image': '//div[@class="model-details"]/img/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '//div[@class="model-details"]//p/span[contains(text(), "Country")]/following-sibling::text()',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//div[@class="model-details"]//p/span[contains(text(), "Height")]/following-sibling::text()',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[@class="model-details"]//p/span[contains(text(), "Weight")]/following-sibling::text()',

        'pagination': '/the-men/list/%s/',
        'external_id': r'model/(.*)/'
    }

    name = 'TimTalesPerformer'
    network = 'Tim Tales'

    start_urls = [
        'https://www.timtales.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "model-list-item")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_height(self, response):
        height = super().get_height(response)
        if "cm" in height.lower():
            height = height.replace(" ", "").lower()
            height = re.search(r'(\d+cm)', height).group(1)
        return height

    def get_weight(self, response):
        weight = super().get_weight(response)
        if "kg" in weight.lower():
            weight = weight.replace(" ", "").lower()
            weight = re.search(r'(\d+kg)', weight).group(1)
        return weight
