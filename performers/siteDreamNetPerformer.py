import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkDreamNetPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "profile-details")]/h3[1]/text()',
        're_name': r'[aA]bout (.*)',
        'image': '//div[contains(@class, "profile-pic")]/img/@src0_1x',
        'image_blob': True,
        'bio': '//strong[contains(text(), "Fun Fact")]/following-sibling::text()',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        're_height': r'(\d+ [cC][mM])',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/tour/models/%s/latest/?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'DreamNetPerformer'
    network = 'Dreamnet'

    start_urls = [
        'https://girls.dreamnet.com',
        'https://www.jizzlocker.com',
        'https://www.selfiesuck.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
