import scrapy
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkDollsHubPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"single-model")]/h2/text()',
        're_name': r'About (.*)',
        'image': '//div[@class="single-mode-box"]/div[@class="row"]/div/img/@src',
        'height': '//div[@class="single-mode-box"]/div[@class="row"]//li[contains(text(), "Height")]/span/text()',
        'weight': '//div[@class="single-mode-box"]/div[@class="row"]//li[contains(text(), "Weight")]/span/text()',
        'haircolor': '//div[@class="single-mode-box"]/div[@class="row"]//li[contains(text(), "Hair")]/span/text()',
        'birthday': '//div[@class="single-mode-box"]/div[@class="row"]//li[contains(text(), "Year")]/span/text()',
        'bio': '//h2[contains(text(), "About")]/following-sibling::p/text()',
        'pagination': '/models?page=%s',
        'external_id': r'models/(.*)/'
    }

    name = 'DollsHubPerformer'
    network = "DollsHub"

    start_urls = [
        'https://www.filthygapers.com',
        'https://www.gynoexclusive.com',
        'https://www.ihuntmycunt.com',
        'https://maturegapers.com',
        'https://www.maturegynoexam.com',
        'https://www.maturegynospy.com',
        'https://www.nastypublicsex.com',
        'https://www.oldsfuckdolls.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="img-slide"][1]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_height(self, response):
        height = super().get_height(response)
        return height + "cm"

    def get_weight(self, response):
        weight = super().get_weight(response)
        return weight + "kg"

    def get_birthday(self, response):
        birthday = super().get_birthday(response)
        if len(birthday) == 4:
            birthday = birthday + "-01-01"
            return dateparser.parse(birthday, date_formats=['%Y-%m-%d'], settings={'TIMEZONE': 'UTC'}).isoformat()
        return None

    def get_name(self, response):
        name = super().get_name(response)
        return name.replace("About ", "").strip()

    def get_nationality(self, response):
        description = self.process_xpath(response, self.get_selector_map('bio'))
        if description:
            description = description.get().lower()
            if "belarus" in description:
                return "Belarusian"
            if "czec" in description:
                return "Czech"
            if "russia" in description:
                return "Russian"
            if "slovaki" in description:
                return "Slovakian"
            if "ukrain" in description:
                return "Ukrainian"
        return None

    def get_birthplace(self, response):
        description = self.process_xpath(response, self.get_selector_map('bio'))
        if description:
            description = description.get().lower()
            if "belarus" in description:
                return "Belarus"
            if "czec" in description:
                return "Czech Republic"
            if "russia" in description:
                return "Russian"
            if "slovaki" in description:
                return "Slovakia"
            if "ukrain" in description:
                return "Ukraine"
        return None
