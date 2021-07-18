import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteFisterTwisterPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@id="frontend"]/div[1]/div[@class="jumbotron"]/h2/strong/text()',
        'image': '//div[@class="row"]/div/img/@src',
        'cupsize': '//dl/dt[contains(text(),"Breast")]/following-sibling::dd[1]/text()',
        'height': '//dl/dt[contains(text(),"Height")]/following-sibling::dd[1]/text()',
        'weight': '//dl/dt[contains(text(),"Weight")]/following-sibling::dd[1]/text()',
        'nationality': '//dl/dt[contains(text(),"Nationality")]/following-sibling::dd[1]/text()',
        'pagination': '/girls/page-%s/?tag=all&sort=recent&pussy=&site=all',
        'external_id': 'models\/(.*).html'
    }

    name = 'FisterTwisterPerformer'
    network = "VIPissy Cash"
    parent = "Fister Twister"

    start_urls = [
        'https://www.fistertwister.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//ul[contains(@class,"media-list")]/li/a')
        for performer in performers:
            imagelink = performer.xpath('./figure/img/@src').get()
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


    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                return cupsize.replace("-","").strip()
        return ''
