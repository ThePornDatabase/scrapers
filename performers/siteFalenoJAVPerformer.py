import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteFalenoJAVPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="bar02"]/h1/span/text()',
        'image': '//div[@class="box_actress02_left"]/img/@src',
        'image_blob': True,
        'birthday': '//div[contains(@class,"box_actress02_list")]/ul[1]/li[1]/p/text()',
        're_birthday': r'(\d{4}/\d{1,2}/\d{1,2})',
        'height': '//div[contains(@class,"box_actress02_list")]/ul[1]/li[2]/p/text()',
        'measurements': '//div[contains(@class,"box_actress02_list")]/ul[1]/li[3]/p/text()',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'FalenoJAVPerformer'
    network = 'Faleno'

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://faleno.jp/top/actress/"
        yield scrapy.Request(link, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_ethnicity(self, response):
        return "Asian"

    def get_performers(self, response):
        performers = response.xpath('//div[@class="img_actress01"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(B\d{2,3}.+?W\d{2,3}.+?H\d{2,3})', measurements):
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

    def get_image(self, response):
        image = super().get_image(response)
        if "?" in image:
            image = re.search(r'(.*)\?', image).group(1)
        return image
