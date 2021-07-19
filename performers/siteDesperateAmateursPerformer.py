import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteDesperateAmateursPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title_bar"][1]/text()',
        'image': '//img[@class="thumbs"]/@src',
        'measurements': '//span[@class="model_info"]/text()[contains(.,"Measurements")]',
        'height': '//span[@class="model_info"]/text()[contains(.,"Height")]',
        'astrology': '//span[@class="model_info"]/text()[contains(.,"Astrological")]',
        'pagination': '/fintour/category.php?id=6&page=%s&s=d&',
        'external_id': 'models\/(.*).html'
    }

    name = 'DesperateAmateursPerformer'
    network = "Desperate Amateurs"
    parent = "Desperate Amateurs"

    start_urls = [
        'https://www.desperateamateurs.com/',
    ]

    def get_performers(self, response):
        performers = response.xpath('//span[@class="update_title"]/a/@href').getall()
        for performer in performers:
            performer = "https://www.desperateamateurs.com/fintour/" + performer
            yield scrapy.Request(performer,callback=self.parse_performer)


    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = re.search('Height:\s?(.*)', height).group(1)
                if height:
                    return height.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search('Measurements:\s?(.*)', measurements).group(1)
                if measurements:
                    return measurements.strip()
        return ''

    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology')).get()
            if astrology:
                astrology = re.search('Sign:\s?(.*)', astrology).group(1)
                if astrology:
                    return astrology.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                if "p16.jpg" not in image:
                    image = "https://www.desperateamateurs.com" + image
                    return image.strip()
        return ''
