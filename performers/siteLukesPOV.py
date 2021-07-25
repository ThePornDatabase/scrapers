import scrapy
import re
import string
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteLukesPOVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//span[contains(@class,"fusion-imageframe")]/img/@src',
        'haircolor': '//strong[contains(text(),"Hair")]/following-sibling::text()',
        'ethnicity': '//strong[contains(text(),"Ethnicity")]/following-sibling::text()',
        'fakeboobs': '//strong[contains(text(),"Tits Type")]/following-sibling::text()',
        'pagination': '/pornstars/page/%s/',
        'external_id': 'models\/(.*).html'
    }

    name = 'LukesPOVPerformer'
    network = "Lukes POV"

    start_urls = [
        'https://lukespov.com/',
    ]

    def get_performers(self, response):
        performers = response.xpath('//h2/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
            if fakeboobs:
                if "enhanced" in fakeboobs.lower():
                    return "Yes"
        return ''

    def get_name(self, response):
        return string.capwords(self.process_xpath(response, self.get_selector_map('name')).get().strip())
