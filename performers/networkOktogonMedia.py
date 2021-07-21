import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from datetime import datetime
import re
import dateparser
import html
import string

class OktogonMediaPerformerSpider(BasePerformerScraper):
    name = 'OktogonMediaPerformer'
    network = 'Oktogon Media'
    parent = 'Oktogon Media'

    start_urls = [
        'https://www.shelovesblack.com',
        'https://www.loveherfeet.com',
    ]

    selector_map = {
        'name': '//div[@class="description"]//h2/text()',
        'image': '//div[@class="bio"]//div[@class="picture"]/img/@src0_3x',
        'bio': '//div[@class="about"]//p/text()',
        'height': '//span[contains(text(),"Height")]/../text()',
        'birthday': '//span[contains(text(),"Date of Birth")]/../text()',
        'date_formats': [ "%B %d, %Y", '%m/%d/%Y', '%m/%d/%y' ],
        'measurements': '//span[contains(text(),"Measurements")]/../text()',
        'cupsize': '//span[contains(text(),"Measurements")]/../text()',
        'ethnicity': '//span[contains(text(),"Ethnicity")]/../text()',
        'haircolor': '//span[contains(text(),"Hair Color")]/../text()',
        'weight': '//span[contains(text(),"Weight")]/../text()',
        'eyecolor': '//span[contains(text(),"Eye Color")]/../text()',
        'fakeboobs': '//span[contains(text(),"Tits Type")]/../text()',
        'tattoos': '//span[contains(text(),"Body Art")]/../text()',
        'pagination': '/tour/models/%s/popular/?gender=female',
        'external_id': 'models\/(.*).html/'
    }

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href,"models/") and contains(@href,".html")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).get()
            if bio != 'This model has no bio':
                return bio.strip()
        return ''

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).getall()
            if haircolor:
                return string.capwords(haircolor[-1].strip())
        return ''

    def get_eyecolor(self, response):
        if 'eyecolor' in self.selector_map:
            eyecolor = self.process_xpath(response, self.get_selector_map('eyecolor')).getall()
            if eyecolor:
                return string.capwords(eyecolor[-1].strip())
        return ''

    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).getall()
            if fakeboobs:
                return string.capwords(fakeboobs[-1].strip())
        return ''

    def get_tattoos(self, response):
        if 'tattoos' in self.selector_map:
            tattoos = self.process_xpath(response, self.get_selector_map('tattoos')).getall()
            if tattoos:
                return string.capwords(tattoos[-1].strip())
        return ''

    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).getall()
            if ethnicity:
                return string.capwords(ethnicity[-1].strip())
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).getall()
            if weight:
                return weight[-1].strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).getall()
            if height:
                return height[-1].strip()
        return ''

    def get_birthday(self, response):
        birthday = self.process_xpath(response, self.get_selector_map('birthday')).getall()
        if birthday:
            date_formats = self.get_selector_map('date_formats')
            birthday = birthday[-1].strip()
            return dateparser.parse(birthday,date_formats=date_formats).isoformat()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            if measurements:
                measurements = html.unescape(measurements[-1].strip())
                measurements = re.findall("(\d{2}[\w]?)", measurements, re.M)
                if len(measurements)==3:
                    return '-'.join(map(str,measurements))
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            if measurements:
                measurements = html.unescape(measurements[-1].strip())
                cupsize = re.search( '^(\d+\w)', measurements )
                if cupsize:
                    return cupsize.group(1)
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search('(http.*.jpg)', image).group(1)
            if image:
                return self.format_link(response, image)
        return ''
