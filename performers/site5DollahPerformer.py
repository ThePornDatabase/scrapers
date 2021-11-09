import re
import warnings
import scrapy
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class Site5DollahPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[contains(@class,"model-page")]/div/div/img/@src',
        'measurements': '//span[@class="item" and contains(text(),"Measurements")]/following-sibling::span[@class="value"][1]/text()',
        'height': '//span[@class="item" and contains(text(),"Height")]/following-sibling::span[@class="value"][1]/text()',
        'weight': '//span[@class="item" and contains(text(),"Weight")]/following-sibling::span[@class="value"][1]/text()',
        'haircolor': '//span[@class="item" and contains(text(),"Hair")]/following-sibling::span[@class="value"][1]/text()',
        'eyecolor': '//span[@class="item" and contains(text(),"Eyes")]/following-sibling::span[@class="value"][1]/text()',
        'ethnicity': '//span[@class="item" and contains(text(),"Ethnicity")]/following-sibling::span[@class="value"][1]/text()',
        'birthday': '//span[@class="item" and contains(text(),"Dob")]/following-sibling::span[@class="value"][1]/text()',
        'pagination': '/models/page%s.html',
        'external_id': r'models/(.*).html'
    }

    name = '5DollahPerformer'
    network = "5Dollah"
    parent = "5Dollah"

    start_urls = [
        'https://www.5dollah.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"models")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site': '5Dollah'}
            )

    def get_gender(self, response):
        return "Female"

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(.*-\d{2}-\d{2})', measurements):
                measurements = measurements.replace(" ", "").strip()
                measurements = re.search(r'(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    cupsize = re.search('(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.upper().strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'\d{2}(?:[a-zA-Z]+)?-\d{2}-\d{2}', measurements):
                return measurements.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cms" in height.lower():
                    height = re.search(r'(\d+)\s+?cm', height.lower()).group(1)
                    if height:
                        height = height + "cm"
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight.lower():
                    weight = re.search(r'(\d+)\s+?kg', weight.lower()).group(1)
                    if weight:
                        weight = weight + "kg"
                        return weight.strip()
        return ''

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            return dateparser.parse(date.strip()).isoformat()
        return ''
