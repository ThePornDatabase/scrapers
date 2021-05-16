import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class VogovPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"info-details")]/h3/text()',
        'image': '//div[contains(@class,"images")]/img/@src',
        'bio': '//article/p/text()',
        'nationality': '//li/span[contains(text(),"Nationality:")]/following-sibling::text()',
        'haircolor': '//li/span[contains(text(),"Hair:")]/following-sibling::text()',
        'eyecolor': '//li/span[contains(text(),"Eyes:")]/following-sibling::text()',
        'measurements': '//li/span[contains(text(),"Measurements:")]/following-sibling::text()',
        'cupsize': '//li/span[contains(text(),"Measurements:")]/following-sibling::text()',
        'height': '//li/span[contains(text(),"Height:")]/following-sibling::text()',
        'weight': '//li/span[contains(text(),"Weight:")]/following-sibling::text()',
        'birthday': '//li/span[contains(text(),"Age:")]/following-sibling::text()',
        'pagination': '/models/%s/',
        'external_id': 'models\/(.*)\/'
    }

    name = 'VogovPerformer'
    network = "Vogov"
    parent = "Vogov"

    start_urls = [
        'https://vogov.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model-post-content")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site':'Vogov'}
            )

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                cupsize = re.search('(.*?)-.*-.*', cupsize).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_birthday(self, response):
        #Birthdate is calculated on Age field.  They're assigned a birthdate of date of import - "Age:" years
        if 'birthday' in self.selector_map:
            age = self.process_xpath(response, self.get_selector_map('birthday')).get()
            age = re.search('(\d{2})\ ', age).group(1)
            if age:
                age = int(age.strip())
                if age >= 18 and age <= 99:
                    birthdate = datetime.now() - relativedelta(years=age)
                    birthdate = birthdate.strftime('%Y-%m-%d')
                    return birthdate
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height:
                    height = re.search('(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ","")
                return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight:
                    weight = re.search('(\d+\s?kg)', weight).group(1).strip()
                    weight = weight.replace(" ","")
                return weight.strip()
        return ''
