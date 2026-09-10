import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkTeenMegaWorldPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "model-profile")]/h1/text()',
        'image': '//div[contains(@class, "model-profile")]/picture/source[contains(@srcset, "2x")]/@srcset',
        'image_blob': True,
        'bio': '//p[contains(@class, "model-profile-about") and contains(@class, "desktop")]//text()',
        'eyecolor': '//dt[normalize-space(.)="Eyes"]/following::*[contains(@class,"model-profile-information-val")][1]/text()',
        'haircolor': '//dt[normalize-space(.)="Hair"]/following::*[contains(@class,"model-profile-information-val")][1]/text()',

        'pagination': '/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'TeenMegaWorldPerformer'
    network = 'TeenMegaWorld'

    start_urls = [
        'https://teenmegaworld.net',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "thumb-profile")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
