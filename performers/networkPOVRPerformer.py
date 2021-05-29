import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class POVRPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[contains(@class,"title")]/text()',
        'image': '//div[contains(@class,"profile") and contains(@class,"logo")]/img/@src',
        'bio': '//div[contains(@class,"profile") and contains(@class,"text")]/p/text()',
        'birthplace': '//div[contains(@class,"profile") and contains(@class,"text")]/div/ul/li/div[contains(text(),"Birth place")]/following-sibling::div/text()',
        'birthday': '//div[contains(@class,"profile") and contains(@class,"text")]/div/ul/li/div[contains(text(),"Birthday")]/following-sibling::div/text()',
        'height': '//div[contains(@class,"profile") and contains(@class,"text")]/div/ul/li/div[contains(text(),"Height")]/following-sibling::div/text()',
        'pagination': '/pornstars?o=d&p=%s',
        'external_id': '.+\/(.*)$'
    }

    name = 'POVRPerformer'
    network = "POVR"
    parent = "POVR"

    start_urls = [
        'https://povr.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="teaser-video"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height:
                    height = re.search('(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ","")
                return height.strip()
        return ''
