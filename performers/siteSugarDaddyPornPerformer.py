import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteSugarDaddyPornPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="crumbs container js-crumbs"]/span[3]/text()',
        'image': '//div[@class="avatar-holder"]//img/@src',
        'cupsize': '//div[@class="question" and contains(text(),"CHEST")]/following-sibling::div/text()',
        'height': '//div[@class="question" and contains(text(),"HEIGHT")]/following-sibling::div/text()',
        'weight': '//div[@class="question" and contains(text(),"WEIGHT")]/following-sibling::div/text()',
        'ethnicity': '//div[@class="question" and contains(text(),"ETHNICITY")]/following-sibling::div/text()',
        'nationality': '//div[@class="question" and contains(text(),"ADDRESS")]/following-sibling::div/text()',
        'bio': '//div[contains(@class,"model-des")]/p/text()',
        'pagination': '/models?page=%s',
        'external_id': 'models\/(.*).html'
    }

    name = 'SugarDaddyPornPerformer'
    network = 'Sugar Daddy Porn'
    parent = 'Sugar Daddy Porn'

    start_urls = [
        'https://www.sugardaddyporn.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return "Female"

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "m" in height.lower():
                    height = re.search('(\d*\.?\d*)\s?m',height.lower()).group(1)
                    if height:
                        height = float(height)
                        height = height*100
                        height = str(height) + "cm"
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight.lower():
                    weight = re.search('(\d+)\s?kg',weight.lower()).group(1)
                    if weight:
                        weight = weight + "kg"
                        return weight.strip()
        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).get()
            if nationality:
                return nationality.replace("\n","").strip()
        return ''


    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).get()
            if bio:
                return bio.replace("\n","").strip()
        return ''

