import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'image': '//img[contains(@class, "model_bio_thumb")]/@src0_2x',
        'image_blob': True,
        'bio': '//div[@class="profile-about"]/p/text()',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        'measurements': '//strong[contains(text(), "Measurements")]/following-sibling::text()',

        'pagination': '/tour/models/%s/latest/?g=',
        'external_id': r'model/(.*)/'
    }

    name = 'SheerAndLacePerformer'
    network = 'SheerAndLace'

    start_urls = [
        'https://sheerandlace.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="item-portrait"]/a')
        for performer in performers:
            meta['name'] = performer.xpath('./@title').get()

            performer = self.format_link(response, performer.xpath('./@href').get())
            yield scrapy.Request(performer, callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.sub(r'[^0-9A-Z-]+', '', measurements.upper())
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search(r'(\d{2,3}[a-zA-Z]+-\d{2}-\d{2})', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    cupsize = re.search('(.*?)-.*', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.upper().strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            height = re.sub(r'[^0-9\'\"]+', '', height)
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
