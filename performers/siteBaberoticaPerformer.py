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
        'name': '//a/h1/text()',
        'image': '//div[@class="m5"]/img/@src',
        'bio': '//div[contains(@class,"th-wrapper")]/div/p/text()',
        'eyecolor': '//div[@id="model"]/div/strong[contains(text(),"Eye")]/../following-sibling::div[1]/text()',
        'haircolor': '//div[@id="model"]/div/strong[contains(text(),"Hair")]/../following-sibling::div[1]/text()',
        'height': '//div[@id="model"]/div/strong[contains(text(),"Height")]/../following-sibling::div[1]/text()',
        'weight': '//div[@id="model"]/div/strong[contains(text(),"Weight")]/../following-sibling::div[1]/text()',
        'birthday': '//div[@id="model"]/div/strong[contains(text(),"Birth")]/../following-sibling::div[1]/text()',
        'ethnicity': '//div[@id="model"]/div/strong[contains(text(),"Ethnicity")]/../following-sibling::div[1]/text()',
        'nationality': '//div[@id="model"]/div/strong[contains(text(),"Country")]/../following-sibling::div[1]/text()',
        'country': '//div[@id="model"]/div/strong[contains(text(),"Country")]/../following-sibling::div[1]/text()',
        'piercings': '//div[@id="model"]/div/strong[contains(text(),"Piercings")]/../following-sibling::div[1]/text()',
        'tattoos': '//div[@id="model"]/div/strong[contains(text(),"Tattoos")]/../following-sibling::div[1]/text()',
        'measurements': '//div[@id="model"]/div/strong[contains(text(),"Body")]/../following-sibling::div[1]/text()',
        'cupsize': '//div[@id="model"]/div/strong[contains(text(),"Breasts")]/../following-sibling::div[1]/text()',
        'aliases': '//div[@id="model"]/div/strong[contains(text(),"Aliases")]/../following-sibling::div[1]/text()',
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
                if "cm" in height and re.match(r'(\d+\s?cm)', height):
                    height = re.search(r'(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ", "")
                if "0 ft" not in height:
                    return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight:
                    weight = re.search(r'(\d+\s?kg)', weight).group(1).strip()
                    weight = weight.replace(" ", "")
                return weight.strip()
        return ''

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        return dateparser.parse(date.strip()).isoformat()
