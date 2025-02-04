import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="updatesBlock"]/h2/text()',
        'image': '//div[contains(@class,"model_picture")]/img/@src0_2x|//div[contains(@class,"model_picture")]/img/@src0_1x',
        'image_blob': True,
        'astrology': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Astrological")]',
        'height': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Height")]',
        'measurements': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Measurements")]',
        'pagination': '/models/models_%s.html?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'GoonMusePerformer'
    network = 'GoonMuse'

    start_urls = [
        'https://www.goonmuse.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.replace("\n", "").replace("\r", "").strip()
                if measurements and re.search(r'(\d+\w+?-\d+-\d+)', measurements):
                    measurements = re.search(r'(\d+\w+?-\d+-\d+)', measurements).group(1)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        cupsize = self.get_measurements(response)
        if cupsize:
            cupsize = re.search(r'(\d+\w+?)-\d+-\d+', cupsize)
            if cupsize:
                return cupsize.group(1)
        return ''

    def get_name(self, response):
        name = super().get_name(response)
        name = string.capwords(name.replace("/", "").replace("\\", "").strip())
        return name

    def get_astrology(self, response):
        astrology = super().get_astrology(response)
        if astrology:
            astrology = astrology.replace("\n", "").replace("\r", "").strip().lower()
            astrology = re.sub(r'[^a-z: ]+', '', astrology)
            astrology = re.search(r'.*:(.*)', astrology)
            if astrology:
                return string.capwords(astrology.group(1).strip())
        return None

    def get_height(self, response):
        height = self.process_xpath(response, self.get_selector_map('height'))
        if height:
            height = height.get()
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'(\d+)\"', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None
