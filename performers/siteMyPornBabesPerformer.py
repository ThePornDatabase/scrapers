import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteMyPornBabesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//dt[contains(text(), "Name:")]/following-sibling::dd[1]/text()',
        'image': '//section[@class="profile"]//img/@src',
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '//script[contains(text(), "getAge")]/text()',
        're_birthday': r'getAge\(\"(\d{4}.*?)\"',
        'birthplace': '',
        'cupsize': '//dt[contains(text(), "Breast")]/following-sibling::dd[1]/text()//script',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//dt[contains(text(), "Height:")]/following-sibling::dd[1]/text()',
        'measurements': '',
        'nationality': '//dt[contains(text(), "Country:")]/following-sibling::dd[1]/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '//dt[contains(text(), "Weight:")]/following-sibling::dd[1]/text()',

        'pagination': '/girls/?modelgallery_id=all&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'MyPornBabesPerformer'
    network = 'My Porn Babes'

    start_urls = [
        'https://mypornbabes.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="contentimg"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
