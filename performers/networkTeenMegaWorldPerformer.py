import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkTeenMegaWorldPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model"]/h1/text()',
        'image': '//div[@class="photo"]/img/@data-src',
        'image_blob': True,
        'bio': '//div[@class="bio"]/div/p/text()',
        'eyecolor': '//div[@class="title" and contains(text(), "Eyes")]/following-sibling::div/text()',
        'haircolor': '//div[@class="title" and contains(text(), "Hair")]/following-sibling::div/text()',

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
        performers = response.xpath('//li[contains(@class,"model_list")]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
