import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSpermManiaSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "scene-array")]/h1/text()',
        'image': '//div[contains(@class, "scene-array")]/img/@src',
        'height': '//div[@class="actress-info"]/div[contains(text(), "Height")]/strong/text()',
        'measurements': '//div[@class="actress-info"]/div[contains(text(), "Sizes")]/strong/text()',
        'pagination': '/girls?page=%s',
        'external_id': r'model\/(.*)/'
    }

    name = 'SpermManiaPerformer'
    network = 'Sperm Mania'
    parent = 'Sperm Mania'
    site = 'Sperm Mania'

    max_pages = 1

    def start_requests(self):
        url = "https://www.spermmania.com/girls"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="actress"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(B\d{2,3}.*? W\d{2,3} H\d{2,3})', measurements):
                bust = re.search(r'B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust) / 2.54)
                waist = re.search(r'W(\d{2,3})', measurements).group(1)
                if waist:
                    waist = round(int(waist) / 2.54)
                hips = re.search(r'H(\d{2,3})', measurements).group(1)
                if hips:
                    hips = round(int(hips) / 2.54)

                if bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)

                if measurements:
                    return measurements.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height and re.search(r'(\d+\s?cm)', height):
                    height = re.search(r'(\d+\s?cm)', height)
                    if height:
                        height = height.group(1).strip()
                        return height.replace(" ", "")
        return ''
