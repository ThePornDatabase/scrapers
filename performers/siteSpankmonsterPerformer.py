import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SpankmonsterPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@id="performer"]/h1/text()|//h1[@class="text-center"]/text()',
        'image': '//picture/source[1]/@srcset',
        'height': '//div[@id="performer"]/ul/li[contains(text(),"Height")]',
        'weight': '//div[@id="performer"]/ul/li[contains(text(),"Weight")]',
        'eyecolor': '//div[@id="performer"]/ul/li[contains(text(),"Eye")]',
        'haircolor': '//div[@id="performer"]/ul/li[contains(text(),"Hair")]',
        'ethnicity': '//div[@id="performer"]/ul/li[contains(text(),"Ethnicity")]',
        'measurements': '//div[@id="performer"]/ul/li[contains(text(),"Meas")]',
        'pagination': '/porn-stars.html?sort=ag_added&page=%s&hybridview=member',
        'external_id': r'models/(.*)/'
    }

    name = 'SpankmonsterPerformer'
    network = "AdultEmpireCash"

    start_urls = [
        'https://spankmonster.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site': 'Spankmonster'}
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search(r':\ (.*)', measurements).group(1)
                if measurements and re.match(r'(.*-.*-.*)', measurements):
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if cupsize:
                cupsize = re.search(r':\ (.*)', cupsize).group(1)
                cupsize = cupsize.strip()
                if cupsize and re.match(r'(.*-.*-.*)', cupsize):
                    cupsize = re.search(r'(.*)-.*-', cupsize).group(1)
            return cupsize

        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = re.search(r'(\d+.*)', height).group(1)
                if height:
                    height = height.replace(" ", "")
                    height = height.replace(".", "")
                    return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                weight = re.search(r'(\d+.*)', weight).group(1)
                if weight:
                    weight = weight.replace(" ", "")
                    weight = weight.replace(".", "")
                    return weight.strip()
        return ''

    def get_eyecolor(self, response):
        if 'eyecolor' in self.selector_map:
            eyecolor = self.process_xpath(response, self.get_selector_map('eyecolor')).get()
            if eyecolor:
                eyecolor = re.search(r':\ (.*)', eyecolor).group(1)
                if eyecolor:
                    return eyecolor.strip()
        return ''

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                haircolor = re.search(r':\ (.*)', haircolor).group(1)
                if haircolor:
                    return haircolor.strip()
        return ''

    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
            if ethnicity:
                ethnicity = re.search(r':\ (.*)', ethnicity).group(1)
                if ethnicity:
                    return ethnicity.strip()
        return ''
