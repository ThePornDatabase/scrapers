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
    
class CosmidPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"profile-details")]/h3[1]/text()',
        'image': '//img[contains(@class,"model_bio_thumb")]/@src0_1x',
        'birthplace': '//strong[contains(text(),"Location")]/following-sibling::text()',
        'haircolor': '//strong[contains(text(),"Hair Color")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'birthday': '//strong[contains(text(),"Age")]/following-sibling::text()',
        'fakeboobs': '//strong[contains(text(),"Boob Type")]/following-sibling::text()',
        'bio': '//div[@class="profile-about"]/p/text()',
        'pagination': '/models/%s/latest/',
        'external_id': 'models/(.+).html$'
    }

    name = 'CosmidPerformer'
    network = 'Cosmid'
    parent = 'Cosmid'

    start_urls = [
        'https://cosmid.net',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            #performer = performer.replace("//", "")
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

        
    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            image = "https://cosmid.net" + image.replace('//','/').strip()
            if image:
                return image.strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                age = birthday.strip()
                birthday = get_birthday_from_age(age)
                return birthday
        return ''        


    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
            if fakeboobs:
                fakeboobs = fakeboobs.strip().lower()
                if "natural" in fakeboobs:
                    return "No"
                else:
                    return "Yes"
        return ''
