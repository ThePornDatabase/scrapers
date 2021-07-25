import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class networkDagfsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="model-thumb-description"]/img/@src',
        'birthday': '//div[@class="model-thumb-description"]//p[contains(text(),"Date Of Birth")]/text()',
        'height': '//div[@class="model-thumb-description"]//p[contains(text(),"Height")]/text()',
        'measurements': '//div[@class="model-thumb-description"]//p[contains(text(),"Measurements")]/text()',
        'pagination': '/models/models_%s.html?g=f',
        'external_id': 'models\/(.*).html'
    }

    name = 'DagfsPerformer'
    network = "dagfs"

    start_urls = [
        'https://bustygfsexposed.com',
        'https://dagfs.com',
        'https://frenchgfs.com',
        'https://realasianexposed.com',
        'https://realblackexposed.com',
        'https://realemoexposed.com',
        'https://realgfsexposed.com',
        'https://reallatinaexposed.com',
        'https://reallesbianexposed.com',
        'https://realmomexposed.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//section[contains(@class,"models")]/ul/li/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"


    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                birthday = birthday.replace("&nbsp;","").replace("\n","").replace("\d","")
                birthday = re.search('Birth:.*?([a-zA-Z].*\d{4})',birthday)
                if birthday:
                    birthday = birthday.group(1)
                    if birthday:
                        birthday = dateparser.parse(birthday.strip()).isoformat()
                        return birthday.strip()
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
