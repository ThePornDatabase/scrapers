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
    
class siteUraLesbianPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-item" and contains(text(), "name")]/span/text()',
        'image': '',
        'height': '//div[@class="profile-item" and contains(text(), "height")]/span/text()',
        'weight': '//div[@class="profile-item" and contains(text(), "weight")]/span/text()',
        'cupsize': '//div[@class="profile-item" and contains(text(), "breast")]/span/text()',
        'birthplace': '//div[@class="profile-item" and contains(text(), "hometown")]/span/text()',
        'pagination': '',
        'external_id': 'model\/(.*)/'
    }

    name = 'AfterSchooljpPerformer'
    network = 'Digital J Media'
    parent = 'After School.jp'
    site = 'After School.jp'

    start_urls = [
        'https://www.afterschool.jp',
    ]


    def start_requests(self):
        url = "https://www.afterschool.jp/en/schoolgirls"
        for link in self.start_urls:
            yield scrapy.Request(url,
                                 callback=self.get_performers,
                                 meta={'page': 1},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = {}
        performers = response.xpath('//div[contains(@class,"girl-block")]')
        for performer in performers:
            image = performer.xpath('./@style').get()
            if image:
                image = re.search('(http.*\.jpg)',image).group(1)
                if image:
                    meta['image'] = image
            performer = performer.xpath('./div/a/@href').get()
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta=meta
            )


    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height and re.search('\d+\s?cm', height):
                    height = re.search('(\d+\s?cm)', height).group(1)
                    height = height.replace(" ","")
                    if height:
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                weight = weight.replace(' ','')
                if "kg" in weight and re.search('\d+kg', weight):
                    weight = re.search('(\d+kg)', weight).group(1)
                    if weight:
                        return weight.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                cupsize = re.search('(.{1,2})\s?cup', cupsize.lower()).group(1)
                if cupsize:
                    return cupsize.strip().upper()
        return ''
