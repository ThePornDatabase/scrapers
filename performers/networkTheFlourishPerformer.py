import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkTheFlourishPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"modelBioArea")]//h2/text()',
        'image': '//div[@class="bioPic"]/img/@src0_1x',
        'image_blob': True,
        'measurements': '//span[@class="data-name" and contains(text(), "Measurements")]/following-sibling::text()',
        'height': '//span[@class="data-name" and contains(text(), "Height")]/following-sibling::text()',
        'bio': '//h3[contains(text(), "About:")]/following-sibling::p/text()',
        'pagination': '/models/models_%s_p.html',
        'external_id': r'models/(.*)/'
    }

    name = 'TheFlourishPerformer'
    network = "The Flourish"

    start_urls = [
        'https://tour.theflourishamateurs.com',
        'https://tour.theflourishfetish.com',
        'https://tour.theflourishpov.com',
        'https://tour.theflourishxxx.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if cupsize:
                cupsize = re.search(r'(\d+\w+)-\d+-\d+', cupsize)
                if cupsize:
                    cupsize = cupsize.group(1)
                    return cupsize.strip().upper()
        return ''
