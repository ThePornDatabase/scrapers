import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class Site18YogaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"model-stats")]//h2/text()',
        'image_blob': True,
        'birthplace': '//h5[contains(text(),"Country")]/../following-sibling::td[1]/text()',
        'height': '//h5[contains(text(),"Height")]/../following-sibling::td[1]/text()',
        're_height': r'([0-9\.]+)',
        'measurements': '//h5[contains(text(),"Measurements")]/../following-sibling::td[1]/text()',
        'pagination': '',
        'external_id': r'girl\/(.*)'
    }

    name = '18YogaPerformer'
    network = "18Yoga"

    start_urls = [
        'https://18yoga.com',
    ]

    def start_requests(self):
        link = "https://18yoga.com/girls"
        yield scrapy.Request(link, callback=self.get_performers, cookies=self.cookies, headers=self.headers)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model-list")]//a')
        for performer in performers:
            meta = {}
            meta['image'] = performer.xpath('./img/@src').get()
            url = performer.xpath("@href").get()
            yield scrapy.Request(url=self.format_link(response, url), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_height(self, response):
        height = super().get_height(response)
        cm = int(float(height) * 30.48)
        return f"{cm}cm"
