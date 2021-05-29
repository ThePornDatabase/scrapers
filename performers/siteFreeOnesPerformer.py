import scrapy
import re
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser

from tpdb.BasePerformerScraper import BasePerformerScraper

class siteFreeOnesPerformerSpider(BasePerformerScraper):

    selector_map = {
        'name': '//div[@data-test="section-personal-information"]/div[@class="p-3"]/text()[1]',
        'image': '//div[contains(@class,"dashboard-image-container")]//img/@src',
        'birthplace': '//p[@class="mb-1 mt-3"]/a/span/text()',
        'nationality': '//a[@data-test="link-country"]/span/text()',
        'ethnicity': '//span[@data-test="link_span_ethnicity"]/text()',
        'eyecolor': '//span[@data-test="link_span_eye_color"]/text()',
        'haircolor': '//span[@data-test="link_span_hair_color"]/text()',
        'height': '//span[@data-test="link_span_height"]/text()',
        'weight': '//span[@data-test="link_span_weight"]/text()',
        'measurements': '//span[@data-test="p-measurements"]/a/span/text()',
        'cupsize': '//span[@data-test="p-measurements"]/a[1]/span/text()',
        'tattoos': '//span[@data-test="p_has_tattoos"]/span/text()',
        'piercings': '//span[@data-test="p_has_piercings"]/span/text()',
        'fakeboobs': '//span[@data-test="link_span_boobs"]/text()',
        'astrology': '//a[contains(@href,"astrologicalSign")]/@href',
        'birthday': '//a[contains(@href,"dateOfBirth")]/@href',
        'bio': '//div[@data-test="biography"]/text()',
        'aliases': '//p[@data-test="p_aliases"]/text()',
        'pagination': '/babes?s=latest&o=desc&p=%s&l=96&f[professions]=porn_stars&f[careerStatus]=active',
        'external_id': '\.ru\/(.*)\/'
    }

    name = 'FreeOnesPerformer'
    network = 'Free Ones'
    parent = 'Free Ones'

    
    start_urls = [
        'https://freeones.ru',
    ]

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href,"/feed")]/@href').getall()
        for performer in performers:
            performer = performer.replace("/feed","/bio")
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )       
    
        
    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height:
                    height = re.search('(.*cm)\ ', height).group(1)
                return height.strip()
        return '' 
        
    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight:
                    weight = re.search('(.*kg)\ ', weight).group(1)
                return weight.strip()
        return '' 


    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                birthday = re.search('(\d{4}-\d{2}-\d{2})', birthday).group(1)
                if birthday:
                    return birthday.strip()
        return ''
        
    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology')).get()
            if astrology:
                astrology = re.search('=(.*)', astrology).group(1)
                if astrology:
                    return astrology.strip().title()
        return ''
        
    def get_gender(self, response):
        return 'Female'
        
    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                if "?c" in image:
                    image = re.search('(.*)\?c',image).group(1)
                if image:
                    return image.strip()
        return ''        

    def get_birthplace(self, response):
        if 'birthplace' in self.selector_map:
            birthplace = self.process_xpath(response, self.get_selector_map('birthplace')).getall()
            birthplace = list(map(lambda x: x.strip(), birthplace))
            birthplacedisplay = ", ".join(birthplace)
            
            return birthplacedisplay
        return ''

    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
            if fakeboobs:
                fakeboobs = fakeboobs.strip().lower()
                if fakeboobs == "fake":
                    fakeboobs = "Yes"
                else:
                    fakeboobs = "No"
                
                return fakeboobs.strip()
        return ''
        
    def get_aliases(self, response):
        if 'aliases' in self.selector_map:
            aliases = self.process_xpath(response, self.get_selector_map('aliases')).get()
            if aliases:
                if "," in aliases:
                    aliases = aliases.split(",")
                    aliases = list(map(lambda x: x.strip(), aliases))
                    return [aliases];
                else:
                    return aliases.strip()
