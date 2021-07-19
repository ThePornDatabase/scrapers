import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteALSAngelsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@id="modelbiodetails"]/h2/text()',
        'image': '',
        'measurements': '//div[@id="modelbiodetails"]/span[contains(text(),"Measurements")]/text()',
        'height': '//div[@id="modelbiodetails"]/span[contains(text(),"Height")]/text()',
        'weight': '//div[@id="modelbiodetails"]/span[contains(text(),"Weight")]/text()',
        'bio': '//div[@id="modelbio"]/p/text()',
        'pagination': '/modelbios.html',
        'external_id': 'models\/(.*).html'
    }

    name = 'ALSAngelsPerformer'
    network = "ALS Angels"
    parent = "ALS Angels"

    start_urls = [
        'http://www.alsangels.com'
    ]
    
    def start_requests(self):
        url = "http://www.alsangels.com/modelbios.html"
        yield scrapy.Request(url,
                             callback=self.get_performers,
                             headers=self.headers,
                             cookies=self.cookies)
                                 
    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelbio"]')
        for performer in performers:
            image = performer.xpath('./a/img/@src').get()
            if image:
                image = "http://www.alsangels.com/" + image.strip()
            performer = performer.xpath('./a/@href').get()
            if performer:
                performer = "http://www.alsangels.com/" + performer
                yield scrapy.Request(performer, callback=self.parse_performer, meta={'image':image})

    def get_gender(self, response):
        return "Female"

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                if re.search('(\(.*cm\))', measurements):
                    measurements = re.sub('(\(.*cm\))','',measurements)
                measurements = measurements.replace("Measurements","").strip()
                measurements = measurements.replace(":","").strip()
                measurements = measurements.replace(" ","").strip()
                if re.search('(.*-\d{2}-\d{2})', measurements):               
                    measurements = re.search('(.*-\d{2}-\d{2})', measurements).group(1)
                    if measurements:
                        cupsize = re.search('(.*?)-.*', measurements).group(1)
                        if cupsize:
                            return cupsize.upper().strip()
        return ''   

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('\d{2}(?:[a-zA-Z]+)?-\d{2}-\d{2}', measurements):
                if re.search('(\(.*cm\))', measurements):
                    measurements = re.sub('(\(.*cm\))','',measurements)            
                measurements = measurements.replace("Measurements","").strip()
                measurements = measurements.replace(":","").strip()
                measurements = measurements.replace(" ","").strip()
                return measurements.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height.lower():
                    height = re.search('(\d+)\s?cm',height.lower()).group(1)
                    if height:
                        height = height+"cm"
                        return height.strip()
                else:
                    height = height.replace("Height","").replace(":","").replace(" ","").strip()
                    return height
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight.lower():
                    weight = re.search('(\d+)\s?kg',weight.lower()).group(1)
                    if weight:
                        weight = weight+"kg"
                        return weight.strip()
                else:
                    weight = weight.replace("Weight","").replace(":","").replace(" ","").strip()
                    return weight
        return ''
        
