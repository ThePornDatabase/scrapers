import scrapy
import re
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser

from tpdb.BasePerformerScraper import BasePerformerScraper

def match_path(argument):
    match = {
        'badoinkvr.com': "/vr-pornstars/%s",
        'babevr.com': "/vrbabes/%s",
        '18vr.com': "/vrgirls/%s",
        'kinkvr.com': "/bdsm-performers/%s",
        'realvr.com': "/pornstars/%s",
        'vrcosplayx.com': "/cosplaygirls/%s",
    }
    return match.get(argument, "")

class networkBadoinkVrPerformerSpider(BasePerformerScraper):

    selector_map = {
        'name': '//ul[contains(@class, "breadcrumbs")]/li[last()]/a/span/text()',
        'image': '//picture/img[@id="girlImage"]/@src',
        'nationality': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Country")]/following-sibling::span/text()',
        'ethnicity': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Ethnicity")]/following-sibling::span/text()',
        'eyecolor': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Eyes")]/following-sibling::span/text()',
        'haircolor': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Hair")]/following-sibling::span/text()',
        'height': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Height")]/following-sibling::span/text()',
        'weight': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Weight")]/following-sibling::span/text()',
        'measurements': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Measurements")]/following-sibling::span/text()',
        'birthday': '//ul[@id="girlOptionDetails"]/li/span[contains(text(),"Age")]/following-sibling::span/text()',
        'bio': '//p[@class="girl-details-bio"]/text()',
        'pagination': '?page=%s&hybridview=member',
        'external_id': r'.*/(.*)/$'
    }

    name = 'BadoinkVrPerformer'
    network = 'Badoink VR'
    parent = 'Badoink VR'


    start_urls = [
        'https://badoinkvr.com',
        'https://babevr.com',
        'https://18vr.com',
        'http://kinkvr.com',
        'https://vrcosplayx.com',
        'https://realvr.com',
    ]

    def get_next_page_url(self, base, page):
        url = urlparse(base)
        match_pagination = match_path(url.netloc)
        return self.format_url(base, match_pagination % page)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="girl-card"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                str_height = re.findall(r'(\d{1,2})', height)
                if len(str_height):
                    feet = int(str_height[0])
                    if len(str_height) > 1:
                        inches = int(str_height[1])
                    else:
                        inches = 0
                    heightcm = str(round(((feet*12)+inches) * 2.54)) + "cm"
                    return heightcm.strip()
        return ''


    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                if "-" in measurements:
                    cupsize = re.search(r'(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.strip()
        return ''

    def get_birthday(self, response):
        #Birthdate is calculated on Age field.  They're assigned a birthdate of date of import - "Age:" years
        if 'birthday' in self.selector_map:
            age = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if age:
                age = re.search(r'(\d+)',age).group(1)
                if age:
                    age = int(age)
                    if age >= 18 and age <= 99:
                        birthdate = datetime.now() - relativedelta(years=age)
                        birthdate = birthdate.strftime('%Y-%m-%d')
                        return birthdate
        return ''

    def get_image(self, response):
        image = super().get_image(response)
        if "?q=" in image:
            image = re.search(r'(.*?)\?q=', image).group(1)
        return image
