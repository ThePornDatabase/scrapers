import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[contains(@class, "entry-title")]/text()',
        'image': '//div[@class="wp-block-image"]/figure/img/@src',
        'image_blob': True,
        'eyecolor': '//td[contains(text(), "Eyes")]/following-sibling::td[1]/text()',
        'height': '//td[contains(text(), "Height")]/following-sibling::td[1]/text()',
        'measurements': '//td[contains(text(), "Meas")]/following-sibling::td[1]/text()',
        'weight': '//td[contains(text(), "Weight")]/following-sibling::td[1]/text()',

        'pagination': '/models/page/%s/',
        'external_id': r'model/(.*)/'
    }

    name = 'PeachyKeenFilmsPerformer'
    network = 'Peachy Keen Films'

    start_urls = [
        'https://pkfstudios.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//article[contains(@class, "posts-entry")]')
        for performer in performers:
            image = performer.xpath('./a/@style')
            if image:
                image = image.get()
                image = re.search(r'(http.*?)\)', image)
                if image:
                    image = image.group(1)
                    meta['image'] = image
                    meta['image_blob'] = self.get_image_blob_from_link(image)
            performer = performer.xpath('./a/@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            return cupsize.strip()
        else:
            if 'measurements' in self.selector_map:
                measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'\d+?\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None

    def get_weight(self, response):
        weight = super().get_weight(response)
        if weight:
            weight = re.search(r'(\d+)', weight)
            if weight:
                weight = weight.group(1)
                weight = int(weight)
                weight = int(weight * .45)
            return str(weight) + "kg"
        return ""
