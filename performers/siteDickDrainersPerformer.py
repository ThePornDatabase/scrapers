import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


def get_birthday_from_age(age):
    age = int(age.strip())
    if age >= 18 and age <= 99:
        birthdate = datetime.now() - relativedelta(years=age)
        birthdate = birthdate.strftime('%Y-%m-%d')
        return birthdate
    return ''

class DickDrainersPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[contains(text(),"About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'birthday': '//strong[contains(text(),"Age")]/following-sibling::text()',
        'pagination': '/tour/models/%s/latest/?g=',
        'external_id': 'models\/(.*).html'
    }

    name = 'DickDrainersPerformer'
    network = "Dick Drainers"
    parent = "Dick Drainers"

    start_urls = [
        'http://www.dickdrainers.com/'
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
                callback=self.parse_performer, meta={'site':'Dick Drainers'}
            )


    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('(.*-\d{2}-\d{2})', measurements):
                measurements = measurements.replace(" ","").strip()
                measurements = re.search('(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    cupsize = re.search('(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.upper().strip()
        return ''   

    def get_bio(self, response):
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('\d{2}(?:[a-zA-Z]+)?-\d{2}-\d{2}', measurements):
                return measurements.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                if " " in image:
                    image = re.search('(.*) ', image).group(1)
                if image:
                    image = image.replace('//','/')
                    image = 'http://www.dickdrainers.com' + image
                    return image.strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            age = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if age:
                age = age.strip()
                return get_birthday_from_age(age)
        return ''
