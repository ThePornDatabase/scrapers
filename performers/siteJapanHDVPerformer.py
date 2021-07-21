import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteJapanHDVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//a/h2/text()',
        'image': '//div[@class="thumb"]/img/@src',
        'bio': '//div[contains(@class,"hidden-xs")]/p/text()',
        'eyecolor': '//div[@id="model"]/div/strong[contains(text(),"Eye")]/../following-sibling::div[1]/text()',
        'haircolor': '//div[@id="model"]/div/strong[contains(text(),"Hair")]/../following-sibling::div[1]/text()',
        'height': '//div[@id="model"]/div/strong[contains(text(),"Height")]/../following-sibling::div[1]/text()',
        'weight': '//div[@id="model"]/div/strong[contains(text(),"Weight")]/../following-sibling::div[1]/text()',
        'birthday': '//div[@id="model"]/div/strong[contains(text(),"Birth")]/../following-sibling::div[1]/text()',
        'ethnicity': '//div[@id="model"]/div/strong[contains(text(),"Ethnicity")]/../following-sibling::div[1]/text()',
        'nationality': '//div[@id="model"]/div/strong[contains(text(),"Country")]/../following-sibling::div[1]/text()',
        'country': '//div[@id="model"]/div/strong[contains(text(),"Country")]/../following-sibling::div[1]/text()',
        'piercings': '//div[@id="model"]/div/strong[contains(text(),"Piercings")]/../following-sibling::div[1]/text()',
        'tattoos': '//div[@id="model"]/div/strong[contains(text(),"Tattoos")]/../following-sibling::div[1]/text()',
        'measurements': '//div[@id="model"]/div/strong[contains(text(),"Body")]/../following-sibling::div[1]/text()',
        'cupsize': '//div[@id="model"]/div/strong[contains(text(),"Breasts")]/../following-sibling::div[1]/text()',
        'aliases': '//div[@id="model"]/div/strong[contains(text(),"Aliases")]/../following-sibling::div[1]/text()',
        'pagination': '/models/page/%s',
        'external_id': 'model\/(.*)/'
    }

    name = 'JapanHDVPerformer'
    network = 'AV Revenue'
    parent = 'JapanHDV'
    site = 'JapanHDV'

    start_urls = [
        'https://japanhdv.com',
    ]


    def start_requests(self):
        url = "https://japanhdv.com/models/"
        for link in self.start_urls:
            yield scrapy.Request(url,
                                 callback=self.get_performers,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href,"/model/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_aliases(self, response):
        image = self.process_xpath(response, self.get_selector_map('aliases')).get()
        if aliases:
            aliases = aliases.split(", ").trim()
            return aliases
        return ''


    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('B\d{2,3}-W\d{2,3}-H\d{2,3}', measurements):
                bust = re.search('B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust)/2.54)
                waist = re.search('W(\d{2,3})', measurements).group(1)
                if waist:
                    waist = round(int(waist)/2.54)
                hips = re.search('H(\d{2,3})', measurements).group(1)
                if hips:
                    hips = round(int(hips)/2.54)
                
                cupsize = response.xpath('//div[@id="model"]/div/strong[contains(text(),"Breasts")]/../following-sibling::div[1]/text()').get()
                if cupsize:
                    if cupsize == "N/A":
                        cupsize = ''
                    else:
                        cupsize = cupsize.strip()

                if bust and waist and hips and cupsize:
                    measurements = str(bust) + cupsize + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
                elif bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('B\d{2,3}-W\d{2,3}-H\d{2,3}', measurements):
                bust = re.search('B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust)/2.54)

                cupsize = response.xpath('//div[@id="model"]/div/strong[contains(text(),"Breasts")]/../following-sibling::div[1]/text()').get()
                if cupsize:
                    if cupsize == "N/A":
                        cupsize = ''
                    else:
                        cupsize = cupsize.strip()

                if bust and cupsize:
                    cupsize = str(bust) + cupsize
                    return cupsize.strip()
                elif cupsize:
                    return cupsize.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https:" + image
            return self.format_link(response, image)
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height and re.match('(\d+\s?cm)', height):
                    height = re.search('(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ","")
                if "0 ft" not in height:
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

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            return dateparser.parse(date.strip()).isoformat()
        else:
            return ''
