import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper


class siteToughLoveXPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="model-name"]/span/following-sibling::text()',
        'image': '//div[@class="model-photo"]/img/@src',
        'birthplace': '//li/span[contains(text(),"birthplace")]/following-sibling::text()',
        'eyecolor': '//li/span[contains(text(),"eyes")]/following-sibling::text()',
        'haircolor': '//li/span[contains(text(),"hair")]/following-sibling::text()',
        'height': '//li/span[contains(text(),"height")]/following-sibling::text()',
        'measurements': '//li/span[contains(text(),"measurements")]/following-sibling::text()',
        'birthday': '//li/span[contains(text(),"birthdate")]/following-sibling::text()',
        'bio': '//li/span[contains(text(),"bio")]/following-sibling::text()',
        'pagination': '/models?page=%s',
        'external_id': 'models/(.+).html$'
    }

    name = 'ToughLoveXPerformer'
    network = 'ToughLoveX'

    start_urls = [
        'https://tour.toughlovex.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//h3[@class="model-name"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                str_height = re.findall('(\d{1,2})', height)
                if len(str_height):
                    feet = int(str_height[0])
                    if len(str_height) > 1:
                        inches = int(str_height[1])
                    else:
                        inches = 0
                    heightcm = str(round(((feet*12)+inches) * 2.54)) + "cm"
                    return heightcm.strip()
        return ''         

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace(" ","").replace(".5","").replace(".","-").strip()
                measurements = re.search('(\d{1,2}[a-zA-Z]+-.+-.+)', measurements).group(1)
                if measurements:
                    if re.search('(.*?)-.*', measurements):
                        cupsize = re.search('(.*?)-.*', measurements).group(1)
                        if cupsize:
                            return cupsize.upper().strip()
        return ''   
    

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace(" ","").replace(".5","").replace(".","-").strip()
                if re.search('(.*-\d{2}-\d{2})', measurements):
                    measurements = re.search('(.*-\d{2}-\d{2})', measurements).group(1)
                    if measurements:
                        return measurements.upper().strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                if re.search('(\d{4}-\d{2}-\d{2})', birthday):
                    return dateparser.parse(birthday.strip(), date_formats=['%Y-%m-%d']).isoformat()                        
        return ''

        
