import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteOopsFamilyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="title-primary"]/text()',
        'image': '//img[contains(@class,"pornstar-detail__picture")]/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '//div[contains(@class, "params--top")]/strong[contains(text(), "Birthday")]/following-sibling::text()[1]',
        're_astrology': r'•(.*)',
        'birthday': '//div[contains(@class, "params--top")]/strong[contains(text(), "Birthday")]/following-sibling::text()[1]',
        're_birthday': r'(\w{3,4} \d{1,2}, \d{4})',
        'birthplace': '//span[@class="pornstar-detail__info--title"]/text()',
        're_birthplace': r'(.*?),',
        'cupsize': '//div[contains(@class, "params--top")]/strong[contains(text(), "Measurements")]/following-sibling::text()[1]',
        're_cupsize': r'(\d{2,3}\w{1,4}?)-\d{2,3}-\d{2,3}',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//div[contains(@class, "params--top")]/strong[contains(text(), "Height")]/following-sibling::text()[1]',
        're_height': r'(\d+ ?cm)',
        'measurements': '//div[contains(@class, "params--top")]/strong[contains(text(), "Measurements")]/following-sibling::text()[1]',
        're_measurements': r'(\d{2,3}\w{1,4}?-\d{2,3}-\d{2,3})',
        'nationality': '//span[@class="pornstar-detail__info--title"]/text()',
        're_nationality': r'(.*?),',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[contains(@class, "params--top")]/strong[contains(text(), "Weight")]/following-sibling::text()[1]',
        're_weight': r'(\d+ ?kg)',

        'pagination': '/model?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'OopsFamilyPerformer'
    network = 'OopsFamily'

    start_urls = [
        'https://oopsfamily.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@class, "pornstar-card")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_astrology(self, response):
        astrology = response.xpath('//div[contains(@class, "params--top")]/strong[contains(text(), "Birthday")]/following-sibling::text()[1]').getall()
        astrology = "".join(astrology)
        astrology = astrology.replace("\n", "").replace("\r", "").replace("\t", "")
        astrology = re.search(r'•(.*)', astrology)
        if astrology:
            return astrology.group(1).strip()
        return None

    def get_height(self, response):
        return super().get_height(response).replace(" ", "")

    def get_weight(self, response):
        return super().get_weight(response).replace(" ", "")
