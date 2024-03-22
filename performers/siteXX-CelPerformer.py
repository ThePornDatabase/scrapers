import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteXXCelPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "model-details")]/h2/text()',
        'image': '//div[contains(@class, "model-details")]/preceding-sibling::div[1]/img/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '//div[contains(@class, "model-details")]//strong[contains(text(), "rom")]/following-sibling::text()[1]',
        'cupsize': '//div[contains(@class, "model-details")]//strong[contains(text(), "reasts")]/following-sibling::text()[1]',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/page-%s/?type=&sort=recent&',
        'external_id': r'model/(.*)/'
    }

    name = 'XX-CelPerformer'
    network = 'XX-Cel'

    start_urls = [
        'https://xx-cel.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "model-cover")]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
