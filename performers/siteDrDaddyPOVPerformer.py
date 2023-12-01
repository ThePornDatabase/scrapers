import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteDrDaddyPOVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="model-name"]/text()',
        'image': '//div[@class="model-thumbnail"]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="model-bio-item"]/text()',
        'astrology': '//b[contains(text(), "Astrological")]/following-sibling::text()',
        'birthday': '//b[contains(text(), "Age")]/following-sibling::text()',
        're_birthday': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'height': '//b[contains(text(), "Height")]/following-sibling::text()',
        're_height': r'(\d+cm)',
        'measurements': '//b[contains(text(), "Measurements")]/following-sibling::text()',
        're_measurements': r'(\d2\w{1,4}-\d{2}-\d{2})',

        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'DrDaddyPOVPerformer'
    network = 'DrDaddyPOV'

    start_urls = [
        'https://drdaddypov.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="pornstar-pic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
