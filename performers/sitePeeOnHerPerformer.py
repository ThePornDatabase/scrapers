import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class sitePeeOnHerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model_box"]/div[@class="filter_box"]/h1[@class="page_title"]/text()',
        'image': '//div[@class="model_img"]/img/@src',
        'cupsize': '//div[@class="sub_con"]/text()',
        'height': '//div[@class="sub_con"]/text()',
        'weight': '//div[@class="sub_con"]/text()',
        'nationality': '//div[@class="sub_con"]/text()',
        'pagination': '/girls/page-%s/?tag=all&sort=recent&pussy=&site=all',
        'external_id': 'models\/(.*).html'
    }

    name = 'PeeOnHerPerformer'
    network = "VIPissy Cash"
    parent = "Pee On Her"

    start_urls = [
        'https://www.peeonher.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"item")]/a')
        for performer in performers:
            imagelink = performer.xpath('./img/@src').get()
            if imagelink:
                meta = {'image':imagelink}
            else:
                meta = {}
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta=meta
            )


    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).getall()
            if height:
                height = "".join(height)
                if "cm" in height.lower():
                    height = re.search('(\d*)\s?cm',height.lower()).group(1)
                    if height:
                        height = height + "cm"
                        return height
                
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).getall()
            if weight:
                weight = "".join(weight)
                if "kg" in weight.lower():
                    weight = re.search('(\d*)\s?kg',weight.lower()).group(1)
                    if weight:
                        weight = weight + "kg"
                        return weight
                
        return ''

    def get_gender(self, response):
        return "Female"


    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).getall()
            if cupsize:
                cupsize = "".join(cupsize)
                cupsize = re.search('Breasts: ([a-zA-Z]{1,3})', cupsize).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).getall()
            if nationality:
                nationality = "".join(nationality)
                nationality = re.search('Country: ([a-zA-Z ]*)', nationality).group(1)
                if nationality:
                    return nationality.strip()
        return ''
