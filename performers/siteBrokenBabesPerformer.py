import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class BrokenBabesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model-bio"]/div/h1/text()',
        'image': '//div[@class="model-thumb-description"]/img/@src',
        'bio': '//div[@class="model-thumb-info"]/h2[@class="second"]/following-sibling::p/text()',
        'height': '//div[@class="model-thumb-info"]/h2/following-sibling::p[contains(text(),"Height")]/text()',
        'measurements': '//div[@class="model-thumb-info"]/h2/following-sibling::p[contains(text(),"Measurements")]/text()',
        'birthday': '//div[@class="model-thumb-info"]/h2/following-sibling::p[contains(text(),"Date Of Birth")]/text()',
        'pagination': '/models/models_%s.html?g=f',
        'external_id': 'models\/(.*).html'
    }

    name = 'BrokenBabesPerformer'
    network = 'Broken Babes'
    parent = 'Broken Babes'
    site = 'Broken Babes'

    start_urls = [
        'https://www.brokenbabes.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//figure/../../a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height:
                    height = re.search('(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ","")
                else:
                    height = re.search('Height:.*\s+(.*)\s+?',height).group(1).strip()
                return height.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search('Measurements:.*\s+(.*?)\s+', measurements).group(1)
                if measurements and re.match('(.*-.*-.*)', measurements):
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search('Measurements:.*\s+(.*?)\s+', measurements).group(1)
                if measurements and re.match('(.*-.*-.*)', measurements):
                    cupsize = re.search('(?:\s+)?(.*)-.*-',measurements).group(1)
                else:
                    cupsize = measurements.strip()
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday and "N/A" not in birthday and "lbs" not in birthday and "Dember" not in birthday:
                birthday = re.search('Date Of Birth:\s+.*?(.*\d{2,4})\s+\(?', birthday).group(1)
                if birthday:
                    return dateparser.parse(birthday.strip()).isoformat()
        return ''


    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return "https://www.brokenbabes.com" + image.strip()
        return ''
