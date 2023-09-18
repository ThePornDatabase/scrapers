import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SitePrivateClassicsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "user-tools")]/preceding-sibling::h1/text()',
        'image': '//div[contains(@class, "pic-model")]/a/img/@src',
        'height': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Height")]/strong/text()',
        'weight': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Weight")]/strong/text()',
        'birthplace': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Birth")]/strong/text()',
        'nationality': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Nationality")]/strong/text()',
        'astrology': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Sign")]/strong/text()',
        'haircolor': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Hair")]/strong/text()',
        'eyecolor': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Eye")]/strong/text()',
        'measurements': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Measurements")]/strong/text()',
        'tattoos': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Tattoos")]/strong/text()',
        'piercings': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Piercings")]/strong/text()',
        'bio': '//div[contains(@class, "user-tools")]/following-sibling::p[contains(@class, "description")]/text()',
        'pagination': '/en/pornstars/%s/',
        'external_id': r'models\/(.*).html'
    }

    name = 'PrivateClassicsPerformer'
    network = 'Private'

    start_urls = [
        'https://www.privateclassics.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//article[contains(@class, "model")]/h1/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                cupsize = re.search(r'(?:\s+)?(.*)-.*-', measurements).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if not height.replace("-", "").strip():
            height = ""
        if "cm" in height:
            height = re.sub('[^a-z0-9]', '', height.lower())
            height = re.search(r'(\d+cm)', height).group(1)
        return height

    def get_weight(self, response):
        weight = super().get_weight(response)
        if not weight.replace("-", "").strip():
            weight = ""
        if "kg" in weight:
            weight = re.sub('[^a-z0-9]', '', weight.lower())
            weight = re.search(r'(\d+kg)', weight).group(1)
        return weight

    def get_tattoos(self, response):
        tattoos = super().get_tattoos(response)
        if not tattoos.replace("-", "").strip():
            tattoos = ""
        return tattoos

    def get_piercings(self, response):
        piercings = super().get_piercings(response)
        if not piercings.replace("-", "").strip():
            piercings = ""
        return piercings
