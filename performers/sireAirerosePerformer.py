import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class AirerosePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="hl"][1]/h1/text()',
        'image': '//div[@class="container marketing"]/div/div/img/@src',
        'bio': '//div[@class="container marketing"]/div/p/text()',
        'ethnicity': '//div[@class="container marketing"]/div/ul/li[contains(text(),"Ethnicity")]/strong/text()',
        'eyecolor': '//div[@class="container marketing"]/div/ul/li[contains(text(),"Eye")]/strong/text()',
        'haircolor': '//div[@class="container marketing"]/div/ul/li[contains(text(),"Hair")]/strong/text()',
        'birthday': '//div[@class="container marketing"]/div/ul/li[contains(text(),"DOB")]/strong/text()',
        'height': '//div[@class="container marketing"]/div/ul/li[contains(text(),"Height")]/strong/text()',
        'weight': '//div[@class="container marketing"]/div/ul/li[contains(text(),"Weight")]/strong/text()',
        'measurements': '//div[@class="container marketing"]/div/ul/li[contains(text(),"Measurements")]/strong/text()',
        'aliases': '//div[@class="container marketing"]/div/ul/li[contains(text(),"AKA")]/strong/text()',
        'pagination': '/pornstars/?page=%s&sort=mostrecent',
        'external_id': '.+\/(.*)$'
    }

    name = 'AirerosePerformer'
    network = "Airerose"
    parent = "Airerose"

    start_urls = [
        'http://airerose.com',
    ]


    def get_aliases(self, response):
        image = self.process_xpath(response, self.get_selector_map('aliases')).get()
        if aliases:
            aliases = aliases.split(", ").trim()
            return aliases
        return ''


    def get_performers(self, response):
        performers = response.xpath('//div[@class="thumbnail"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date and "Unknown" not in date:
            return dateparser.parse(date.strip()).isoformat()
        return ''
        
    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height and "Unknown" not in height:
                if "'" in height:
                    feet = int(re.search('(\d+)\'(\d+)',height.replace(" ","")).group(1))
                    inches = int(re.search('(\d+)\'(\d+)',height.replace(" ","")).group(2))
                    heightcm = str(round(((feet*12)+inches) * 2.54)) + "cm"
                    return heightcm
                    
                return height.strip()
        return ''        
        
        
    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight and re.match('\d+', weight):
                weight = re.search('(\d+)', weight).group(1)
                weight = int(weight)
                if weight:
                    weight = str(round(weight*.453592)) + "kg"
                    return weight
                    
                return weight.strip()
        return ''        
        

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                cupsize = re.search('(?:\s+)?(.*)-.*-',measurements).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''
