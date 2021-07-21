import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper


def get_birthday_from_age(age):
    age = int(age.strip())
    if age >= 18 and age <= 99:
        birthdate = datetime.now() - relativedelta(years=age)
        birthdate = birthdate.strftime('%Y-%m-%d')
        return birthdate
    return ''
    
class siteGirlsRimmingPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2/a/following-sibling::text()',
        'image': '//img[contains(@class,"model_bio_thumb")]/@src0_1x',
        
        'height': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Height")]',
        'eyecolor': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Eyes")]',
        'haircolor': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Hair")]',
        'nationality': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Nationality")]',
        'birthday': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Age")]',
        'bio': '//span[@class="model_bio_heading"]/following-sibling::comment()[contains(.,"Bio Extra Field") and not(contains(.,"Accompanying"))]/following-sibling::text()',
        
        'pagination': '/tour/models/%s/popular/?gender=female',
        'external_id': 'models/(.+).html$'
    }

    name = 'GirlsRimmingPerformer'
    network = 'Girls Rimming'
    parent = 'Girls Rimming'

    start_urls = [
        'https://www.girlsrimming.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_name(self, response):
        
        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = re.sub('[^a-zA-Z0-9 ]','',name)
        return name.strip()

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height.lower():
                    height = re.search('(\d+)\s?cm',height.lower())
                    if height:
                        height = height.group(1)
                        height = height+"cm"
                        return height.strip()
                else:
                    height = height.replace("Height","").replace(":","").replace(" ","").strip()
                    return height
        return ''
        

    def get_eyecolor(self, response):
        if 'eyecolor' in self.selector_map:
            eyecolor = self.process_xpath(response, self.get_selector_map('eyecolor')).get()
            if eyecolor:
                eyecolor = eyecolor.replace("&nbsp;", "").replace("\n", "")
                eyecolor = re.search('Eyes:\s+(.*?)\s{3}', eyecolor)
                if eyecolor:
                    eyecolor = eyecolor.group(1)
                    return eyecolor.strip()
        return ''

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                haircolor = haircolor.replace("&nbsp;", "").replace("\n", "")
                haircolor = re.search('Hair:\s+(.*?)\s{3}', haircolor)
                if haircolor:
                    haircolor = haircolor.group(1)
                    return haircolor.strip()
        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).get()
            if nationality:
                nationality = nationality.replace("&nbsp;", "").replace("\n", "")
                nationality = re.search('Nationality:\s+(.*?)\s{3}', nationality)
                if nationality:
                    nationality = nationality.group(1)
                    return nationality.strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                birthday = birthday.replace("&nbsp;", "").replace("\n", "")
                birthday = re.search('Birthday:\s+(.*?)\s{3}', birthday)
                if birthday:
                    birthday = birthday.group(1)
                    age = birthday.strip()
                    birthday = get_birthday_from_age(age)
                    return birthday
        return ''
