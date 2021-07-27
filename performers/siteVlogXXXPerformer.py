import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

class siteVlogXXXPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="model-bio-pic"]/img/@src0_1x',
        'height': '//b[contains(text(),"Height")]/following-sibling::text()[1]',
        'measurements': '//b[contains(text(),"Measurements")]/following-sibling::text()[1]',
        'astrology': '//b[contains(text(),"Astrological")]/following-sibling::text()[1]',
        'piercings': '//b[contains(text(),"Body Art")]/following-sibling::text()[1]',
        'tattoos': '//b[contains(text(),"Body Art")]/following-sibling::text()[1]',
        'eyecolor': '//b[contains(text(),"Eye")]/following-sibling::text()[1]',
        'haircolor': '//b[contains(text(),"Hair")]/following-sibling::text()[1]',
        'ethnicity': '//b[contains(text(),"Ethnicity")]/following-sibling::text()[1]',
        'birthday': '//b[contains(text(),"Date of Birth")]/following-sibling::text()[1]',
        'nationality': '//b[contains(text(),"Nationality")]/following-sibling::text()[1]',
        'bio': '//p[@class="descriptionText"]/text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': 'models\/(.*)\/'
    }

    name = 'VlogXXXPerformer'
    network = "VlogXXX"

    start_urls = [
        'https://vlogxxx.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"pornstar-pic")]/a[contains(@href,"/models/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = re.search('(\d{3}\s?cm)', height).group(1)
                if height:
                    height = height.replace(" ","")
                    return height.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('(\d+\w+-\d+-\d+)', measurements):
                    measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if cupsize:
                cupsize = re.search('(\d+\w+)-\d+-\d+', cupsize).group(1)
                if cupsize:
                    return cupsize.strip().upper()
        return ''
 
 
    def get_tattoos(self, response):
        if 'tattoos' in self.selector_map:
            tattoos = self.process_xpath(response, self.get_selector_map('tattoos')).get()
            if tattoos:
                if "tattoo" in tattoos.lower():
                    return "Yes"
                else:
                    return "No"
        return ''

    def get_piercings(self, response):
        if 'piercings' in self.selector_map:
            piercings = self.process_xpath(response, self.get_selector_map('piercings')).get()
            if piercings:
                if "piercing" in piercings.lower():
                    return "Yes"
                else:
                    return "No"
        return ''
        

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            return dateparser.parse(date).isoformat()

        return None        
