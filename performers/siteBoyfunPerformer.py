import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
true = True
false = False


class SiteBoyfunPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/span[@class="title"]/text()',
        'image': '//div[@class="model-thumb"]/img/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '//span[@class="label" and contains(text(), "Nationality")]/following-sibling::span/text()',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//span[@class="label" and contains(text(), "Height")]/following-sibling::span/text()',
        're_height': r'(\d+ cm)',
        'measurements': '',
        'nationality': '//span[@class="label" and contains(text(), "Nationality")]/following-sibling::span/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '//span[@class="label" and contains(text(), "Weight")]/following-sibling::span/text()',
        're_weight': r'(\d+ kg)',

        'pagination': '/models/page%s.html',
        'external_id': r'model/(.*)/'
    }

    cookies = [{"domain":"www.boyfun.com","hostOnly":true,"httpOnly":false,"name":"warningHidden","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"hide"}]

    name = 'BoyfunPerformer'
    network = 'Boyfun'

    start_urls = [
        'https://www.boyfun.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-inside"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
