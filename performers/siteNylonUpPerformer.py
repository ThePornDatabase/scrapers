import string
import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteNylonUpPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "profile-details")]/h3[contains(text(), "About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'eyecolor': '//strong[contains(text(), "Eyes")]/following-sibling::span/text()',
        'haircolor': '//strong[contains(text(), "Hair")]/following-sibling::span/text()',
        'height': '//strong[contains(text(), "Height")]/following-sibling::span/text()',
        'measurements': '//strong[contains(text(), "Measurements")]/following-sibling::span/text()',
        'nationality': '//strong[contains(text(), "Country")]/following-sibling::span/text()',
        'pagination': '/tour/models/%s/popular/?g=f',
        'external_id': r'model\/(.*)/'
    }

    name = 'NylonUpPerformer'
    network = 'Nylon Up'

    max_pages = 1

    start_urls = [
        'https://www.nylonup.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).getall()
        name = " ".join(name).replace("About", "")
        return string.capwords(name.strip())

    def get_gender(self, response):
        return 'Female'

    def get_height(self, response):
        height = super().get_height(response)
        height = re.search(r'(\d{2,3})', height)
        if height:
            height = height.group(1) + "cm"
        return height

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'\d{2,3}/\d{2,3}/\d{2,3}', measurements):
                measures = re.findall(r'(\d{2,3})', measurements)
                if len(measures) == 3:
                    bust = measures[0]
                    waist = measures[1]
                    hips = measures[2]
                if bust:
                    bust = round(int(bust) / 2.54)
                if waist:
                    waist = round(int(waist) / 2.54)
                if hips:
                    hips = round(int(hips) / 2.54)

                if bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
        return ''
