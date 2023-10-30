import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteScorelandPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//section[contains(@id, "model-page")]//h1/text()',
        're_name': r'(.*)\'',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '//span[contains(text(), "Bra Size")]/following-sibling::span/text()',
        'ethnicity': '//span[contains(text(), "Ethnicity")]/following-sibling::span/text()',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '//span[contains(text(), "Hair Color")]/following-sibling::span/text()',
        'height': '//span[contains(text(), "Height")]/following-sibling::span/text()',
        'measurements': '//span[contains(text(), "Measurements")]/following-sibling::span/text()',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//span[contains(text(), "Weight")]/following-sibling::span/text()',

        'pagination': '/big-boob-models/?page=%s',
        'external_id': r'model/(.*)/'
    }

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        # ~ 'DOWNLOAD_DELAY': 60,
        # ~ 'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    name = 'ScorelandPerformer'
    network = 'ScorePass'

    start_urls = [
        'https://www.scoreland.com',
        'https://www.scoreland2.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class, "info")]/div[contains(@class, "trunc")]/a/@href').getall()
        for performer in performers:
            if "?nats" in performer:
                performer = re.search(r'(.*?)\?nats', performer).group(1)
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+?-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+?-\d+-\d+)', measurements).group(1)
                cupsize = self.get_cupsize(response)
                if cupsize:
                    measurements = re.search(r'\d+\w+?(-\d+-\d+)', measurements).group(1)
                    measurements = cupsize.upper() + measurements
                return measurements.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'\d+?\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None

    def get_weight(self, response):
        weight = super().get_height(response)
        if weight:
            weight = re.search(r'(\d+)', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .453592)) + "kg"
                return weight
        return None
