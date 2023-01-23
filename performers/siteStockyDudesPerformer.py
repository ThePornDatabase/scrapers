import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteStockyDudesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="frame"]//div[@id="profName"]/text()',
        'image': '//div[@class="frame"]//div[@class="profImages"]/img[1]/@src',
        'image_blob': True,
        'bio': '//div[@class="frame"]//div[@id="profAbout"]/span/text()',
        'gender': '',
        'astrology': '//table//td[contains(text(), "SIGN")]/following-sibling::td/text()',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//table//td[contains(text(), "HEIGHT")]/following-sibling::td/text()',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//table//td[contains(text(), "WEIGHT")]/following-sibling::td/text()',

        'pagination': '/models?Page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'StockyDudesPerformer'
    network = 'Stocky Dudes'

    start_urls = [
        'https://www.stockydudes.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="lstDudeImg"]/img/@data-href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
