import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteVIPissyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[@class="title"]/span/text()',
        'image': '//div[@class="row"]/div/img/@src',
        'cupsize': '//dl[@class="row"]/dt[contains(text(),"Breast")]/following-sibling::dd[1]/text()',
        'height': '//dl[@class="row"]/dt[contains(text(),"Height")]/following-sibling::dd[1]/text()',
        'weight': '//dl[@class="row"]/dt[contains(text(),"Weight")]/following-sibling::dd[1]/text()',
        'nationality': '//dl[@class="row"]/dt[contains(text(),"Nationality")]/following-sibling::dd[1]/text()',
        'pagination': '/girls/page-%s/?tag=&sort=recent',
        'external_id': 'models\/(.*).html'
    }

    name = 'VIPissyPerformer'
    network = "VIPissy Cash"
    parent = "VIPissy"

    start_urls = [
        'https://www.vipissy.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//figure/a')
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
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height.lower():
                    height = re.search('(\d*)\s?cm',height.lower()).group(1)
                    if height:
                        height = height + "cm"
                
                return height
                
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight.lower():
                    weight = re.search('(\d*)\s?kg',weight.lower()).group(1)
                    if weight:
                        weight = weight + "kg"
                
                return weight
                
        return ''

    def get_gender(self, response):
        return "Female"
