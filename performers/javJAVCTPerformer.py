import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class JavJAVCTPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//li[contains(@class, "breadcrumb__item--active")]/text()',
        'image': '//div[@class="stats"]/img/@data-src',
        'image_blob': True,
        'birthday': '//div[@class="stats"]/ul/li[contains(./text(), "Born:")]/text()',
        're_birthday': r': (.*)',
        'height': '//div[@class="stats"]/ul/li[contains(./text(), "Height:")]/text()',
        're_height': r': (.*)',
        'measurements': 'InCode',

        'pagination': '/models/pg-%s',
        'external_id': r'model/(.*)/'
    }

    name = 'JAVJAVCTPerformer'
    network = 'R18'

    start_urls = [
        'https://javct.net',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//h3[contains(@class,"card__title")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        bust = response.xpath('//div[@class="stats"]/ul/li[contains(./text(), "Breast:")]/text()')
        waist = response.xpath('//div[@class="stats"]/ul/li[contains(./text(), "Waist:")]/text()')
        hips = response.xpath('//div[@class="stats"]/ul/li[contains(./text(), "Hips:")]/text()')

        if bust and waist and hips:
            bust = re.search(r'(\d+)', bust.get())
            if bust:
                bust = bust.group(1)
            waist = re.search(r'(\d+)', waist.get())
            if waist:
                waist = waist.group(1)
            hips = re.search(r'(\d+)', hips.get())
            if hips:
                hips = hips.group(1)
            if bust and waist and hips:
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

    def get_cupsize(self, response):
        bust = response.xpath('//div[@class="stats"]/ul/li[contains(./text(), "Breast:")]/text()')
        if bust:
            bust = re.search(r'(\d+)', bust.get())
            if bust:
                bust = bust.group(1)
                if bust:
                    bust = round(int(bust) / 2.54)
                if bust:
                    return str(bust)
        return ''

    def get_name(self, response):
        name = super().get_name(response)
        if "(" in name:
            name = re.search(r'(.*?)\(', name).group(1)
        return string.capwords(name.strip())

    def get_height(self, response):
        height = super().get_height(response)
        return height.replace(" ", "")
