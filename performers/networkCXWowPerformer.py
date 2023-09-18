import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkCXWowPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="graybox"]/div[contains(@class,"titlebox")]/h3[1]/span/text()',
        'image': '//div[contains(@class,"profileimg")]//img/@src',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '//span[contains(text(), "strological")]/following-sibling::text()[1]',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//span[contains(text(), "eight")]/following-sibling::text()[1]',
        'measurements': '//span[contains(text(), "easure")]/following-sibling::text()[1]',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/tour/categories/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'CXWowPerformer'
    network = 'CX Wow'

    start_urls = [
        # ~ 'https://www.becomingfemme.com/',
        # ~ 'https://www.pure-bbw.com/',
        # ~ 'https://www.pure-ts.com/',
        # ~ 'https://www.pure-xxx.com/',
        'https://www.tspov.com/',
    ]

    def get_gender(self, response):
        if "pure-bbw" in response.url:
            return 'Female'
        if "pure-ts" in response.url or "tspov" in response.url or "becmoingfemme" in response.url:
            return 'Transgender Female'
        return None

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "models")]//a[contains(@href, "/models/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            return cupsize.strip()
        else:
            if 'measurements' in self.selector_map:
                measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip().upper()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if "'" in height:
            height = re.sub(r'[^0-9\']', '', height)
            feet = re.search(r'(\d+)\'', height)
            if feet:
                feet = feet.group(1)
                feet = int(feet) * 12
            else:
                feet = 0
            inches = re.search(r'\'(\d+)', height)
            if inches:
                inches = inches.group(1)
                inches = int(inches)
            else:
                inches = 0
            return str(int((feet + inches) * 2.54))
        return None
