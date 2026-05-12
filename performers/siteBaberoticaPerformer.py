import re
import warnings
import dateparser
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class BaberoticaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model-photo"]/img/@alt',
        'image': '//div[@class="model-photo"]/img/@src',
        'bio': '//div[@class="header-model"]/div[@class="info"]/p//text()',
        'eyecolor': '//div[@class="model-profile" and contains(./strong/text(), "Eye")]/text()',
        'haircolor': '//div[@class="model-profile" and contains(./strong/text(), "Hair")]/text()',
        'height': '//div[@class="model-profile" and contains(./strong/text(), "Height")]/text()',
        'weight': '//div[@class="model-profile" and contains(./strong/text(), "Weight")]/text()',
        'birthday': '//div[@class="model-profile" and contains(./strong/text(), "Birth")]/text()',
        'ethnicity': '//div[@class="model-profile" and contains(./strong/text(), "Ethnicity")]/text()',
        'nationality': '//div[@class="model-profile" and contains(./strong/text(), "Country")]/text()',
        'country': '//div[@class="model-profile" and contains(./strong/text(), "Country")]/text()',
        'piercings': '//div[@class="model-profile" and contains(./strong/text(), "Piercings")]/text()',
        'tattoos': '//div[@class="model-profile" and contains(./strong/text(), "Tattoos")]/text()',
        'measurements': '//div[@class="model-profile" and contains(./strong/text(), "Body")]/text()',
        'cupsize': '//div[@class="model-profile" and contains(./strong/text(), "Breasts")]/text()',
        'aliases': '//div[@class="model-profile" and contains(./strong/text(), "Alias")]/text()',
        'pagination': '/models/page/%s',
        'external_id': r'model\/(.*)/'
    }

    name = 'BaberoticaPerformer'
    network = 'Baberotica'
    parent = 'Baberotica'
    site = 'Baberotica'

    start_urls = [
        'https://baberotica.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href,"/model/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_aliases(self, response):
        aliases = self.process_xpath(response, self.get_selector_map('aliases')).get()
        if aliases:
            aliases = aliases.split(", ").trim()
            return aliases
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'\d+.*?-.*?\d+.*?-.*?\d+', measurements):
                measurements = measurements.replace("B", "").replace("W", "").replace("H", "")
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                if 'measurements' in self.selector_map:
                    measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                    if measurements and re.match(r'\d+.*?-.*?\d+.*?-.*?\d+', measurements):
                        breasts = re.search(r'(\d+).*?-.*?\d+.*?-.*?\d+', measurements).group(1)
                        cupsize = breasts.strip() + cupsize.strip()
                        if cupsize:
                            return cupsize.strip()
                return cupsize.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https:" + image
            return self.format_link(response, image)
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = re.sub(r'[^a-z0-9]+', '', height.lower())
                if "cm" in height.lower():
                    height = re.search(r'(\d+cm)', height.lower())
                    if height:
                        return height.group(1).strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                weight = re.sub(r'[^a-z0-9]+', '', weight.lower())
                if "kg" in weight.lower():
                    weight = re.search(r'(\d+kg)', weight.lower())
                    if weight:
                        return weight.group(1).strip()
        return ''
