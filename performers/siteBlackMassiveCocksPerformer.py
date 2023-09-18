import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBlackMassiveCocksPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '//li[contains(text(), "Ethnicity")]/text()',
        're_ethnicity': r'Ethnicity: (.*)',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '//li[contains(text(), "Hair")]/text()',
        're_haircolor': r'Hair: (.*)',
        'height': '',
        'measurements': '//li[contains(text(), "Meas")]/text()',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/black-massive-cocks-porn-stars.html?page=%s&hybridview=member',
        'external_id': r'model/(.*)/'
    }

    name = 'BlackMassiveCocksPerformer'
    network = 'West Coast Productions'

    start_urls = [
        'https://blackmassivecocks.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="grid-item"]')
        for performer in performers:
            image = performer.xpath('.//picture/source/@data-srcset')
            if image:
                image = image.get()
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)
            performer = self.format_link(response, performer.xpath('./a/@href').get())
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.strip()
                if re.search(r'(\d+\w+?-\d+-\d+)', measurements):
                    measurements = re.search(r'(\d+\w+?-\d+-\d+)', measurements).group(1)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.strip()
                if re.search(r'(\d+\w+?-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+?)-\d+-\d+', measurements).group(1)
                    if cupsize:
                        return cupsize.strip()
        return ''

    def get_weight(self, response):
        weight = response.xpath('//li[contains(text(), "Weight")]/text()')
        if weight:
            weight = weight.get()
            weight = re.search(r'(\d+) lbs', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .453592)) + "kg"
                return weight
        return None

    def get_height(self, response):
        height = response.xpath('//li[contains(text(), "Height")]/text()')
        if height:
            height = height.get()
            if re.search(r'(\d+) ft.*?(\d+) in', height):
                height = re.search(r'(\d+) ft.*?(\d+) in', height)
                feet = height.group(1)
                feet = int(feet) * 12
                inches = height.group(2)
                inches = int(inches)
                height = str(int((feet + inches) * 2.54)) + "cm"
                return height
        return None
