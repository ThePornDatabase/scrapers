import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class siteSlaveToBondagePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profileDetails"]//h2[@class="title"]/text()',
        'image': '//div[@class="profilePic"]//img/@src0_3x',
        'image_blob': True,
        'bio': '//div[@class="profileContent"]/p//text()',
        'pagination': '/tour/models/%s/latest/',
        'external_id': r'model/(.*)/'
    }

    name = 'siteSlaveToBondagePerformer'
    network = 'SlaveToBondage'

    start_urls = [
        'https://www.slavetobondage.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="slave"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
