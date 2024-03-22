import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteAdultAllStarsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="updatesBlock"]/div/h2/text()',
        'image': '//div[contains(@class, "model_picture")]/img/@src0_3x|//div[contains(@class, "model_picture")]/img/@src0_2x|//div[contains(@class, "model_picture")]/img/@src0_1x',
        'image_blob': True,
        'bio': '//comment()[contains(.,"Bio Extra Field")]/following-sibling::p/text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'AdultAllStarsPerformer'
    network = 'Adult All Stars'

    start_urls = [
        'https://www.adultallstars.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "modelPic")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_name(self, response):
        name = super().get_name(response)
        name = name.replace("/", "").strip()
        return name

    def get_astrology(self, response):
        astrology = response.xpath('//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(., "Astrological")]')
        if astrology:
            astrology = astrology.getall()
            astrology = "".join(astrology)
            astrology = astrology.replace("\n", "").replace("\r", "").replace("\t", "")
            astrology = re.search(r'Sign:(.*)', astrology)
            if astrology:
                astrology = astrology.group(1)
                return astrology.strip()
        return None

    def get_nationality(self, response):
        nationality = response.xpath('//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(., "Nationality")]')
        if nationality:
            nationality = nationality.getall()
            nationality = "".join(nationality)
            nationality = nationality.replace("\n", "").replace("\r", "").replace("\t", "")
            nationality = re.search(r'Nationality:(.*)', nationality)
            if nationality:
                nationality = nationality.group(1)
                return nationality.strip()
        return None
