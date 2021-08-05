import scrapy
import re
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser

from tpdb.BasePerformerScraper import BasePerformerScraper

class sitePinupFilesPerformerSpider(BasePerformerScraper):

    selector_map = {
        'name': '//h1/text()',
        'image': '//div[contains(@class,"model-picture")]/img/@src0_1x',
        'birthplace': '//p[@class="mb-1 mt-3"]/a/span/text()',
        'nationality': '//strong[contains(text(),"Country")]/following-sibling::text()',
        'ethnicity': '//strong[contains(text(),"Ethnicity")]/following-sibling::text()',
        'eyecolor': '//strong[contains(text(),"Eye")]/following-sibling::text()',
        'haircolor': '//strong[contains(text(),"Hair")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'weight': '//strong[contains(text(),"Weight")]/following-sibling::text()',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'tattoos': '//strong[contains(text(),"Tattoos")]/following-sibling::text()',
        'piercings': '//strong[contains(text(),"Piercings")]/following-sibling::text()',
        'fakeboobs': '//strong[contains(text(),"Real Breasts")]/following-sibling::i/@class',
        'astrology': '//a[contains(@href,"astrologicalSign")]/@href',
        'birthday': '//strong[contains(text(),"Birthday")]/following-sibling::text()',
        'bio': '//div[@class="update-info-block"]/p/text()',
        'pagination': '/models/%s/latest/',
        'external_id': '\.ru\/(.*)\/'
    }

    name = 'PinupFilesPerformer'
    network = 'Pinup Files'

    
    start_urls = [
        'https://www.pinupfiles.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )       


    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                try:
                    birthday = dateparser.parse(birthday.strip()).isoformat()
                    if birthday:
                        return birthday.strip()
                except:
                    return ''
        return ''
        
    def get_gender(self, response):
        return 'Female'

    def get_fakeboobs(self, response):
        fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
        if fakeboobs:
            fakeboobs = "No"
        else:
            fakeboobs = "Yes"
            
        return fakeboobs

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
