import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSlimk4kPerformerSpider(BasePerformerScraper):
    name = 'Slim4kPerformer'
    network = 'Slim4k'

    start_urls = [
        'https://www.slim4k.com',
    ]

    selector_map = {
        'name': '//h2/text()',
        'image': '',
        'measurements': '//ul[@class="model-list"]/li[contains(text(), "Parameters")]/span/text()',
        'astrology': '//ul[@class="model-list"]/li[contains(text(), "Zodiac")]/span/text()',
        'height': '//ul[@class="model-list"]/li[contains(text(), "Height")]/span/text()',
        'weight': '//ul[@class="model-list"]/li[contains(text(), "Weight")]/span/text()',
        'cupsize': '//ul[@class="model-list"]/li[contains(text(), "Breast")]/span/text()',
        'pagination': '/models/%s/',
        'external_id': r'girls/(.+)/?$'
    }

    def get_gender(self, response):
        return "Female"

    def get_performers(self, response):
        performers = response.xpath('//div[@id="list_models_models_list_items"]/a')
        for performer in performers:
            image = performer.xpath('./div/img/@src').get().replace(" ", "%20")
            if not image:
                image = ''
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'image': image}
            )

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize'))
            if cupsize:
                cupsize = cupsize.get()
                if "n/a" not in cupsize.lower():
                    measurements = self.process_xpath(response, self.get_selector_map('measurements'))
                    if measurements:
                        measurements = measurements.get()
                        if re.search(r'(\d{2,3})-(\d{2,3})-(\d{2,3})', measurements):
                            measurements = re.search(r'(\d{2,3})-(\d{2,3})-(\d{2,3})', measurements)
                            bust = str(round(int(measurements.group(1)) / 2.54))
                            if bust and cupsize:
                                return bust + cupsize
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                if re.search(r'(\d{2,3})-(\d{2,3})-(\d{2,3})', measurements):
                    measurements = re.search(r'(\d{2,3})-(\d{2,3})-(\d{2,3})', measurements)
                    bust = str(round(int(measurements.group(1)) / 2.54))
                    hips = str(round(int(measurements.group(2)) / 2.54))
                    waist = str(round(int(measurements.group(3)) / 2.54))
                    if bust and hips and waist:
                        return bust + "-" + hips + "-" + waist
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height'))
            if height:
                height = height.get()
                if re.search(r'(\d+)', height):
                    return height.strip() + "cm"
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight'))
            if weight:
                weight = weight.get()
                if re.search(r'(\d+)', weight):
                    return weight.strip() + "kg"
        return ''

    def get_astrology(self, response):
        astrology = super().get_astrology(response)
        if "n/a" not in astrology.lower():
            return astrology.title()
        return ''
