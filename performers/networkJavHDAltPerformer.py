import re
import dateparser
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkJavHDAltPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title"]/h1/text()|//div[@class="b-model"]/header[@class="b-content-header"]/h2[@class="b-content-title"]/text()',
        'image': '//div[@class="model"]/div/a/img/@src|//div[@class="b-model-info"]/a/img[@class="b-thumb-img"]/@src',
        'height': '//ul[@class="params models_items"]/li/span[contains(text(), "Height")]/following-sibling::text()|//strong[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//ul[@class="params models_items"]/li/span[contains(text(), "Weight")]/following-sibling::text()|//strong[contains(text(), "Weight")]/following-sibling::text()',
        'haircolor': '//ul[@class="params models_items"]/li/span[contains(text(), "Hair")]/following-sibling::text()|//strong[contains(text(), "Hair")]/following-sibling::text()',
        'eyecolor': '//ul[@class="params models_items"]/li/span[contains(text(), "Eye")]/following-sibling::text()|//strong[contains(text(), "Eye")]/following-sibling::text()',
        'ethnicity': '//ul[@class="params models_items"]/li/span[contains(text(), "Ethnicity")]/following-sibling::text()|//strong[contains(text(), "Ethnicity")]/following-sibling::text()',
        'birthplace': '//ul[@class="params models_items"]/li/span[contains(text(), "Birth place")]/following-sibling::text()|//strong[contains(text(), "Birth place")]/following-sibling::text()',
        'fakeboobs': '//ul[@class="params models_items"]/li/span[contains(text(), "Breast factor")]/following-sibling::text()|//strong[contains(text(), "Breast factor")]/following-sibling::text()',
        'birthday': '//ul[@class="params models_items"]/li//i[@itemprop="birthDate"]/text()|//strong[contains(text(), "Birth date")]/following-sibling::text()',
        'measurements': '//ul[@class="params models_items"]/li/span[contains(text(), "Measurements")]/following-sibling::text()|//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'pagination': '/en/models/justadded/%s',
        'external_id': r'model/(.*)/'
    }

    name = 'JavHDAltPerformer'
    network = 'JavHD'

    start_urls = [
        'https://av69.tv',
        'https://avanal.com',
        'https://avstockings.com',
        'https://avtits.com',
        'https://ferame.com',
        'https://gangav.com',
        'https://hairyav.com',
        'https://heymilf.com',
        'https://heyoutdoor.com',
        'https://lingerieav.com',
        'https://pussyav.com',
        'https://schoolgirlshd.com',
        'https://shiofuky.com',
    ]

    cookies = {
        'locale': 'en',
    }

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="thumb-body"]/a[contains(@href, "/model/")]/@href|//div[@class="b-thumb"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'\d{2,3}-\d{2,3}-\d{2,3}', measurements):
                measures = re.findall(r'(\d{2,3})', measurements)
                if len(measures) == 3:
                    bust = measures[0]
                    waist = measures[1]
                    hips = measures[2]
                if bust:
                    bust = round(int(bust) / 2.54)
                if waist:
                    waist = round(int(waist) / 2.54)
                if hips:
                    hips = round(int(hips) / 2.54)

                if bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height'))
            if height:
                height = height.get()
                if "cm" in height and re.match(r'(\d+\s?cm)', height):
                    height = re.search(r'(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ", "")
                    if height:
                        return height.strip()
        return ''

    def get_weight(self, response):
        weight = super().get_weight(response)
        return weight + "kg"

    def get_name(self, response):
        name = super().get_name(response)
        name = name.replace("Av Idol", "").strip()
        name = name.replace("Anal Sex Videos", "").strip()
        name = name.replace("In Sexy Stockings", "").strip()
        name = name.replace("Hairy Pics & Vids", "").strip()
        name = name.replace("Pussy Pics", "").strip()
        name = name.replace("Outdoor Sex Scenes", "").strip()
        name = name.replace("Blowjob", "").strip()
        name = name.replace("At Shiofuky.com", "").strip()
        name = name.replace("Gangbang", "").strip()
        name = name.replace("Videos", "").strip()
        name = name.replace("Pictures", "").strip()
        name = name.replace("And", "").strip()
        return name.encode("ascii", "ignore").decode()

    def get_birthday(self, response):
        birthday = super().get_birthday(response)
        if birthday:
            birthday = dateparser.parse(birthday, date_formats=['%d %B %Y'], settings={'TIMEZONE': 'UTC'}).isoformat()
        return birthday

    def get_birthplace(self, response):
        birthplace = super().get_birthplace(response)
        if birthplace == "N/A":
            birthplace = ""
        if birthplace:
            birthplace = birthplace.title()
        return birthplace

    def get_fakeboobs(self, response):
        fakeboobs = super().get_fakeboobs(response)
        if fakeboobs:
            if fakeboobs == "Silicon":
                return "True"
        return None
