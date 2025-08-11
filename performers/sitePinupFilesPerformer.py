import scrapy
import re
from scrapy import Selector
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class sitePinupFilesPerformerSpider(BasePerformerScraper):

    selector_map = {
        'name': '//h1/text()',
        'image': '//div[contains(@class,"model-picture")]/img/@src0_1x',
        'birthplace': '//p[@class="mb-1 mt-3"]/a/span/text()',
        'nationality': '//strong[contains(text(),"Country")]/following-sibling::text()',
        'ethnicity': '//strong[contains(text(),"Ethnicity")]/following-sibling::text()',
        'eyecolor': '//strong[contains(text(),"Eye")]/following-sibling::text()',
        'haircolor': '//strong[contains(text(),"Hair")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'weight': '//strong[contains(text(),"Weight")]/following-sibling::text()',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'tattoos': '//strong[contains(text(),"Tattoos")]/following-sibling::text()',
        'piercings': '//strong[contains(text(),"Piercings")]/following-sibling::text()',
        'fakeboobs': '//strong[contains(text(),"Real Breasts")]/following-sibling::i/@class',
        'astrology': '//a[contains(@href,"astrologicalSign")]/@href',
        'birthday': '//strong[contains(text(),"Birthday")]/following-sibling::text()',
        'bio': '//div[@class="update-info-block"]/p/text()',
        'pagination': '/models/%s/latest/',
        'external_id': r'\.ru/(.*)/'
    }

    cookies = {"name": "warn", "value": "true"}

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'CONCURRENT_REQUESTS_PER_IP': 2,
        'RETRY_ENABLED': False,
        "HTTPERROR_ALLOWED_CODES": [500],
    }

    name = 'PinupFilesPerformer'
    site = 'Pinup Dollars'
    parent = 'Pinup Dollars'
    network = 'Pinup Dollars'

    start_urls = [
        'https://www.pinupfiles.com',
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        index_text = response.text.replace("\r", "").replace("\n", "").replace("\t", "")
        index_text = re.sub(r'\s+', ' ', index_text)
        index_text = re.sub(r'^.*?\<!', '<!', index_text)
        index_text = Selector(text=index_text)
        performers = index_text.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                try:
                    birthday = dateparser.parse(birthday.strip()).isoformat()
                    if birthday:
                        return birthday.strip()
                except:
                    return ''
        return ''

    def get_gender(self, response):
        return 'Female'

    def get_fakeboobs(self, response):
        fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
        if fakeboobs:
            fakeboobs = "No"
        else:
            fakeboobs = "Yes"

        return fakeboobs

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search(r'(\d{2,3}[a-zA-Z]+-\d{2}-\d{2})', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    cupsize = re.search('(.*?)-.*', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.upper().strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = re.search(r'(\d{2,3}[a-zA-Z]+-\d{2}-\d{2})', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    return measurements.upper().strip()
        return ''

    def get_height(self, response):
        height = response.xpath('//strong[contains(text(),"Height")]/following-sibling::text()')
        if height:
            height = height.get()
            height = re.sub(r'[^0-9\']+', '', height)
            height = re.search(r'(\d+?\'\d+)', height)
            if height:
                height = height.group(1)
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
