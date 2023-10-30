import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteS3xusPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'bio': '//meta[@property="og:description"]/@content',
        'birthday': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Birthdate")]/../p/text()',
        'birthplace': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Born")]/../p/text()',
        'eyecolor': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Eyes")]/../p/text()',
        'haircolor': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Hair")]/../p/text()',
        'height': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Height")]/../p/text()',
        'measurements': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Measurements")]/../p/text()',
        'weight': '//div[contains(@class, "model-spec")]/ul/li/h3[contains(text(), "Weight")]/../p/text()',

        'pagination': '/models?page=%s&order_by=publish_dates&sort_by=desc',
        'external_id': r'models/(.*)/'
    }

    name = 'S3xusPerformer'

    start_urls = [
        'https://www.s3xus.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model-card"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

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

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                return measurements.strip()
        return ''
