import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteEroticDesirePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="content"]/div[1]//img/@src',
        'image_blob': True,
        'bio': '//h1/following-sibling::p/text()',
        'ethnicity': '//h1/following-sibling::div[@class="row"]//strong[contains(text(), "Ethnicity")]/following-sibling::text()[1]',
        'eyecolor': '//h1/following-sibling::div[@class="row"]//strong[contains(text(), "Eye Color")]/following-sibling::text()[1]',
        'haircolor': '//h1/following-sibling::div[@class="row"]//strong[contains(text(), "Hair Color")]/following-sibling::text()[1]',
        'height': '//h1/following-sibling::div[@class="row"]//strong[contains(text(), "Height")]/following-sibling::text()[1]',
        'measurements': '//h1/following-sibling::div[@class="row"]//strong[contains(text(), "Measurements")]/following-sibling::text()[1]',
        'weight': '//h1/following-sibling::div[@class="row"]//strong[contains(text(), "Weight")]/following-sibling::text()[1]',

        'pagination': '/models/latest?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'EroticDesirePerformer'
    network = 'Erotic Desire'

    start_urls = [
        'https://eroticdesire.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "card_model")]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = re.sub(r'[^a-z0-9]+', '', measurements.get().lower())
                if measurements:
                    bust = re.search(r'bust(\d{2,3})', measurements).group(1)
                    if bust:
                        bust = round(int(bust) / 2.54)
                    waist = re.search(r'waist(\d{2,3})', measurements).group(1)
                    if waist:
                        waist = round(int(waist) / 2.54)
                    hips = re.search(r'hips(\d{2,3})', measurements).group(1)
                    if hips:
                        hips = round(int(hips) / 2.54)

                    if bust and waist and hips:
                        measurements = str(bust) + "-" + str(waist) + "-" + str(hips)

                    if measurements:
                        return measurements.strip()
        return ''

    def get_cupsize(self, response):
        cupsize = self.get_measurements(response)
        if cupsize:
            cupsize = re.search(r'(\d+)-.*', cupsize)
            if cupsize:
                return cupsize.group(1)
        return ''

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'(\d+)', weight)
        if weight:
            return weight.group(1) + "kg"
        return None

    def get_height(self, response):
        height = super().get_height(response)
        height = re.search(r'(\d+)', height)
        if height:
            return height.group(1) + "cm"
        return None
