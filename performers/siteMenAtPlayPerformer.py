import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

class SiteMenAtPlaySpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="heroTitle"]/h2/text()',
        're_name': r'(.*)? [vV]ital',
        'image': '//div[@class="model_picture"]/img/@src0_1x|//div[@class="model_picture"]/img/@src',
        'bio': '//div[@class="heroTitle"]/following-sibling::p/text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': 'models\/(.*)\/'
    }

    name = 'MenAtPlayPerformer'
    network = "Men At Play"

    start_urls = [
        'https://menatplay.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_height(self, response):
        height = self.get_text(response)
        height = re.search(r'eight:.+?\|(.*?)\|', height)
        if height:
            return height.group(1)
        return ''

    def get_nationality(self, response):
        nationality = self.get_text(response)
        nationality = re.search(r'ationality:.+?\|(.*?)\|', nationality)
        if nationality:
            return nationality.group(1)
        return ''

    def get_eyecolor(self, response):
        eyecolor = self.get_text(response)
        eyecolor = re.search(r'Eye Color:.+?\|(.*?)\|', eyecolor)
        if eyecolor:
            return eyecolor.group(1)
        return ''

    def get_haircolor(self, response):
        haircolor = self.get_text(response)
        haircolor = re.search(r'Hair Color:.+?\|(.*?)\|', haircolor)
        if haircolor:
            return haircolor.group(1)
        return ''

    def get_text(self, response):
        text = response.xpath('//div[@class="heroTitle"]/following-sibling::text()').getall()
        text = "".join(text)
        text = text.replace("<br />", "|")
        text = text.replace("&nbsp;", "")
        text = text.replace("\r", "").replace("\n", "|").replace("\t", "").replace("  ", " ")
        text = text.replace(" |", "|")
        return text


