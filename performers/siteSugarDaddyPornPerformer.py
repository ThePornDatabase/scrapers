import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSugarDaddyPornPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"crumbs container")]/span[3]/text()',
        'image': '//div[contains(@class, "avatar")]//img/@src',
        'cupsize': '//li[contains(@class,"physique-data") and p[contains(text(), "Chest")]]/p[@class="answer"]/text()',
        'height': '//li[contains(@class,"physique-data") and p[contains(text(), "Height")]]/p[@class="answer"]/text()',
        'weight': '//li[contains(@class,"physique-data") and p[contains(text(), "Weight")]]/p[@class="answer"]/text()',
        'ethnicity': '//li[contains(@class,"physique-data") and p[contains(text(), "Ethnicity")]]/p[@class="answer"]/text()',
        'nationality': '//li[contains(@class,"physique-data") and p[contains(text(), "Address")]]/p[@class="answer"]/text()',
        'bio': '//p[@class="model__description"]/text()',
        'pagination': '/models/%s',
        'external_id': r'models/(.*).html'
    }

    name = 'SugarDaddyPornPerformer'
    network = 'Sugar Daddy Porn'
    parent = 'Sugar Daddy Porn'

    start_urls = [
        'https://www.sugardaddyporn.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//article[contains(@class, "model")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return "Female"

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "m" in height.lower():
                    height = re.search(r'(\d*\.?\d*)\s?m', height.lower()).group(1)
                    if height:
                        height = float(height)
                        height = height * 100
                        height = str(height) + "cm"
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight')).get()
            if weight:
                if "kg" in weight.lower():
                    weight = re.search(r'(\d+)\s?kg', weight.lower()).group(1)
                    if weight:
                        weight = weight + "kg"
                        return weight.strip()
        return ''

    def get_nationality(self, response):
        if 'nationality' in self.selector_map:
            nationality = self.process_xpath(response, self.get_selector_map('nationality')).get()
            if nationality:
                return nationality.replace("\n", "").strip()
        return ''

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).get()
            if bio:
                return bio.replace("\n", "").strip()
        return ''
