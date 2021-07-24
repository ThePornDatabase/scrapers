import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

class siteBrickYatesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[contains(text(),"About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_3x',
        'cupsize': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'weight': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'astrology': '//strong[contains(text(),"Sign")]/following-sibling::text()',
        'eyecolor': '//strong[contains(text(),"Eye")]/following-sibling::text()',
        'birthplace': '//strong[contains(text(),"From")]/following-sibling::text()',
        'pagination': '/tour/models/%s/latest/?g=f',
        'external_id': 'models\/(.*).html'
    }

    name = 'BrickYatesPerformer'
    network = "Brick Yates"

    start_urls = [
        'http://www.brickyates.com/'
    ]


    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = name.replace("About", "").strip()
        return name
        
    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return "Female"

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if measurements:
                measurements = measurements.replace(" ","").replace(".","").lower()
                if re.search('(\d+lbs)', measurements):
                    strip = re.search('(\d+lbs)', measurements).group(1)
                    cupsize = measurements.replace(strip,"")
                    if cupsize and re.search('(\d+[a-z])', cupsize):
                        return cupsize.upper().strip()
        return ''   
        

    def get_weight(self, response):
        if 'cupsize' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if measurements:
                measurements = measurements.replace(" ","").replace(".","").lower()
                if re.search('(\d+lbs)', measurements):
                    weight = re.search('(\d+lbs)', measurements).group(1)
                    if weight:
                        return weight.strip()
        return ''   
        
    def get_bio(self, response):
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if not image:
                image = response.xpath('//div[@class="profile-pic"]/img/@src0_2x').get()
            if not image:
                image = response.xpath('//div[@class="profile-pic"]/img/@src0_1x').get()
            if image:
                return image.strip()
        return ''

