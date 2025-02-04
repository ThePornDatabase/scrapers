import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteFreshmenPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model_card"]//h2/text()',
        'image': '//div[@class="model_card"]//img[contains(@src, "jpg")]/@src',
        'image_blob': True,
        'bio': '//div[@class="model_card"]//h2/following-sibling::p/text()',
        'astrology': '//div[@class="model_card"]//th[contains(text(), "Zodiac")]/following-sibling::th[1]/text()',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//div[@class="model_card"]//th[contains(text(), "Eye")]/following-sibling::th[1]/text()',
        'fakeboobs': '',
        'haircolor': '//div[@class="model_card"]//th[contains(text(), "Hair")]/following-sibling::th[1]/text()',
        'height': '//div[@class="model_card"]//th[contains(text(), "Height")]/following-sibling::th[1]/text()',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[@class="model_card"]//th[contains(text(), "Weight")]/following-sibling::th[1]/text()',

        'pagination': '/models?p=%s&case=getPage',
        'external_id': r'model/(.*)/'
    }

    name = 'FreshmenPerformer'
    network = 'Freshmen'

    start_urls = [
        'https://www.freshmen.net',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model_item"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
