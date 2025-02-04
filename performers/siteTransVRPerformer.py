import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteTransVRPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[@class="modelname"]/text()',
        'image': '//div[@class="model_photo"]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="model_details clear"]/div[@id="bio"]/ul[1]/li[1]/text()',
        'ethnicity': '//div[@class="model_details clear"]//b[contains(text(), "Ethnicity")]/following-sibling::text()',
        'nationality': '//div[@class="model_details clear"]//b[contains(text(), "Nationality")]/following-sibling::text()',

        'pagination': '/tour/models/%s/latest/?g=',
        'external_id': r'model/(.*)/'
    }

    name = 'TransVRPerformer'
    network = 'Grooby Network'

    start_urls = [
        'https://www.transvr.com',
    ]

    def get_gender(self, response):
        return 'Trans Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelphoto"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
