import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkDreamCashPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="item-name"]/span/text()',
        'image': '//img[contains(@class, "model_bio_thumb ")]/@src0_1x',
        'image_blob': True,
        'bio': '//p[@class="description"]/text()',
        'gender': '',
        'birthplace': '//ul[@class="content-details"]/li[contains(., "Location")]/b/text()',
        'haircolor': '//ul[@class="content-details"]/li[contains(., "Hair")]/b/text()',
        'nationality': '//ul[@class="content-details"]/li[contains(., "Location")]/b/text()',

        'pagination': '/t4/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'DreamCashPerformer'
    network = 'Dream Cash'

    start_urls = [
        'https://www.teendreams.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "model-item")]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_cupsize(self, response):
        cupsize = response.xpath('//ul[@class="content-details"]/li[contains(., "Tits")]/b/text()')
        if cupsize:
            cupsize = cupsize.get()
            cupsize = re.search(r'^(\d+\w+)', cupsize)
            if cupsize:
                return cupsize.group(1).upper()
        return None

    def get_image(self, response):
        image = super().get_image(response)
        if "-1x" in image:
            image = image.replace("-1x", "-full")
        return image
