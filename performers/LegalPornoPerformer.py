import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser

from tpdb.BasePerformerScraper import BasePerformerScraper

# Performer images have tokens

class LegalPornoPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[@class="text-danger"]/text()',
        'image': '//div[@class="model--avatar"]/img/@src',
        'nationality': '//td[@class="text-danger"]/a[contains(@href,"nationality")]/text()',
        'birthday': '//td[contains(text(),"Age:")]/following-sibling::td[@class="text-danger"]/text()',
        'haircolor': '//td[@class="text-danger"]/a[contains(@href,"niche")]/text()',
        'pagination': '/model/list/sort/release/pageNumber/%s',
        'external_id': 'model\/(\d*)\/',
    }

    name = 'LegalPornoPerformer'
    network = 'Legal Porno'
    parent = 'Legal Porno'

    start_urls = [
        'https://analvids.com/',
        'https://pornworld.com/',
    ]

    def get_gender(self, response):
        return 'Female'
        
    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"thumbnail-model")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get()
        if not name:
            name = re.search('\d+\/(.*)$', response.url).group(1)
            name = name.replace("_"," ").title()
            
        return name.strip()

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return image.strip()
        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).get()
            if nationality:
                return nationality.strip()
        return ''

    def get_birthday(self, response):
        #Birthdate is calculated on Age field.  They're assigned a birthdate of date of import - "Age:" years
        if 'birthday' in self.selector_map:
            age = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if age:
                age = re.search('(\d+)',age).group(1)
                if age:
                    age = int(age)
                    if age >= 18 and age <= 99:
                        birthdate = datetime.now() - relativedelta(years=age)
                        birthdate = birthdate.strftime('%Y-%m-%d')
                        return birthdate
        return ''
        
    def get_haircolor(self,response):
        tags = response.xpath('//td[@class="text-danger"]/a[contains(@href,"niche")]/text()').getall()
        if "blonde" in tags:
            return "Blonde"
        if "brunette" in tags:
            return "Brunette"
        if "redheads" in tags:
            return "Redhead"
        if "black hair" in tags:
            return "Black"
      
        return ''
        
    def get_eyecolor(self,response):
        tags = response.xpath('//td[@class="text-danger"]/a[contains(@href,"niche")]/text()').getall()
        if "blue eye" in tags:
            return "Blue"
        if "brown eye" in tags:
            return "Brown"
        if "green eye" in tags:
            return "Green"
      
        return ''

    def get_fakeboobs(self, response):
        tags = response.xpath('//td[@class="text-danger"]/a[contains(@href,"niche")]/text()').getall()
        if "fake tits" in tags:
            return "Yes"
        if "natural tits" in tags:
            return "No"
        return ''
        
    def get_ethnicity(self, response):
        tags = response.xpath('//td[@class="text-danger"]/a[contains(@href,"niche")]/text()').getall()
        if "black women" in tags:
            return "Black"
        if "asian" in tags:
            return "Asian"
        if "white skin" in tags or "pale white skin" in tags:
            return "Caucasian"
        return ''        
