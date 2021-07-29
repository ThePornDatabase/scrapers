import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper


class siteHeavyOnHottiesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h4/text()',
        'image': '//div[contains(@class,"comment-section")]/div/img/@src',
        'birthplace': '//div[contains(@class,"comment-section")]/div/h5/text()',
        'height': '//div[contains(@class,"comment-section")]/div/p[1]/text()',
        'weight': '//div[contains(@class,"comment-section")]/div/p[1]/text()',
        'bio': '//div[contains(@class,"comment-section")]/div/p[2]/text()',
        'pagination': '/models/page-%s/?tag=&sort=recent&',
        'external_id': 'models/(.+).html$'
    }

    name = 'HeavyOnHottiesPerformer'
    network = 'Heavy On Hotties'

    start_urls = [
        'https://www.heavyonhotties.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model-cover")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height.lower():
                    height = re.search('(\d+)\s+?cm',height.lower()).group(1)
                    if height:
                        height = height+"cm"
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight.lower():
                    weight = re.search('(\d+)\s+?kg',weight.lower()).group(1)
                    if weight:
                        weight = weight+"kg"
                        return weight.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return "https:" + image.strip()
        return ''


    def get_birthplace(self, response):
        if 'birthplace' in self.selector_map:
            birthplace = self.process_xpath(response, self.get_selector_map('birthplace')).get()
            if birthplace:
                birthplace = birthplace.replace('From:', '')
                if re.search('(, \d+)', birthplace):
                    birthplace = re.search('(.*), \d+', birthplace).group(1)
            if birthplace:
                return birthplace.strip()
        return ''

