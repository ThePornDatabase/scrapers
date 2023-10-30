import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkLegalPornoPornworldPerformerSpider(BasePerformerScraper):
    name = 'PornworldPerformer'
    network = 'Legal Porno'

    selector_map = {
        'name': '//h1[@class="model__title"]/text()',
        'image': '//div[contains(@class, "model__left--photo")]/img/@src',
        'image_blob': True,
        'nationality': '//td[contains(text(), "Nationality")]/following-sibling::td[1]/div/a/text()',

        'pagination': '/models/sex/female/page/%s/',
        'external_id': r'model/(.*)/'
    }

    start_urls = [
        'https://pornworld.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model-top"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
