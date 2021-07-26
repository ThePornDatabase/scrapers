import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from datetime import datetime
import re
import dateparser
import html
import string

class SiteHollyRandallPerformerSpider(BasePerformerScraper):
    name = 'HollyRandallPerformer'
    network = 'Holly Randall'

    start_urls = [
        'https://www.hollyrandall.com',
    ]

    selector_map = {
        'name': '//div[contains(@class,"modelBioArea")]//h2/text()',
        'image': '//div[@class="bioPic"]/img/@src0_3x',
        'height': '//span[contains(text(),"Height")]/following-sibling::text()',
        'astrology': '//span[contains(text(),"Sign")]/following-sibling::text()',
        'birthplace': '//span[contains(text(),"Place of Birth")]/following-sibling::text()',
        'haircolor': '//span[contains(text(),"Hair")]/following-sibling::text()',
        'eyecolor': '//span[contains(text(),"Eyes")]/following-sibling::text()',
        'birthday': '//span[contains(text(),"Date of Birth")]/following-sibling::text()',
        'measurements': '//span[contains(text(),"Measurements")]/following-sibling::text()',
        'cupsize': '//span[contains(text(),"Measurements")]/../text()',
        'pagination': '/models/models_%s.html',
        'external_id': '/models/models_%s.html'
    }

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return self.format_link(response, image.strip())
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = re.search('(\d+\s?cm)', height)
                if height:
                    height = height.group(1)
                    return height.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search('(\d{2,3}[a-zA-Z]+-\d{2}-\d{2})', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    cupsize = re.search('(.*?)-.*', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.upper().strip()
        return ''   
    

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search('(\d{2,3}[a-zA-Z]+-\d{2}-\d{2})', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    return measurements.upper().strip()
        return ''
