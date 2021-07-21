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
        'name': '//h1[1]/text()',
        'image': '//style[contains(text(),"girl")]/text()',
        'height': '//div[@id="data"]/strong[contains(text(),"Height")]/following-sibling::text()[1]',
        'birthday': '//div[@id="data"]/strong[contains(text(),"Age")]/following-sibling::text()[1]',
        'measurements': '//div[@id="data"]/strong[contains(text(),"Measurements")]/following-sibling::text()[1]',
        'birthplace': '//div[@id="data"]/img[contains(@src,"from.png")]/following-sibling::text()[1]',
        'pagination': '',
        'external_id': 'model\/(.*)/'
    }

    name = 'UraLesbianPerformer'
    network = 'Digital J Media'
    parent = 'Ura Lesbian'
    site = 'Ura Lesbian'

    start_urls = [
        'https://www.uralesbian.com',
    ]


    def start_requests(self):
        url = "https://www.uralesbian.com/getmodels.php?l=0&s=1&q="
        for link in self.start_urls:
            yield scrapy.Request(url,
                                 callback=self.get_performers,
                                 meta={'page': 1},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model-obj"]/div[@class="model-img"]/a/@href').getall()
        for performer in performers:
            performer = "https://www.uralesbian.com/" + performer
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('B\d{2,3}.W\d{2,3}.H\d{2,3}', measurements.strip()):
                
                bust = re.search('B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust)/2.54)

                waist = re.search('W(\d{2,3})', measurements).group(1)
                if waist:
                    waist = round(int(waist)/2.54)

                hips = re.search('H(\d{2,3})', measurements).group(1)
                if hips:
                    hips = round(int(hips)/2.54)
                
                if bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search('(http.*.jpg)', image).group(1)
            if image:
                return self.format_link(response, image)
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height and re.match('(\d+\s?cm)', height):
                    height = re.search('(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ","")
                    if height:
                        return height.strip()
        return ''

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                age = re.search('^(\d+)', birthday.strip()).group(1)
                if age:
                    age = age.strip()
                    birthday = get_birthday_from_age(age)
                    return birthday
        return ''

    def get_birthplace(self, response):
        if 'birthplace' in self.selector_map:
            birthplace = self.process_xpath(response, self.get_selector_map('birthplace')).get()
            if birthplace:
                birthplace = birthplace.lower().replace("from", "").strip().title()
                return birthplace.strip()
        return ''
