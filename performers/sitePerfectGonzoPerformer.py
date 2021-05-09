import scrapy
import re

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerfectGonzoPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[@class="mg-md"]/text()',
        'image': "//div[contains(@class,'bigmodelpic')]/img/@src",
        'nationality': '//strong[contains(text(),"Nationality")]/following-sibling::text()[1]',
        'ethnicity': '//strong[contains(text(),"Ethnicity")]/following-sibling::text()[1]',
        'tattoos': '//strong[contains(text(),"Addons")]/following-sibling::text()[1]',
        'piercings': '//strong[contains(text(),"Addons")]/following-sibling::text()[1]',
        'pagination': '/models/page-%s/?tag=&sort=alpha&pussy=all&',
        'external_id': 'models\/(.+)?$'
    }

    name = 'PerfectGonzoPerformer'
    network = "DEV8 Entertainment"
    parent = "DEV8 Entertainment"

    start_urls = [
        'https://www.perfectgonzo.com/',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_id(self, response):
        search = re.search(self.get_selector_map('external_id'), response.url, re.IGNORECASE).group(1)
        if "?nats" in search:
            search = re.search('(.*)\?nats',search).group(1)
        return search
        
    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelitem"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_nationality(self, response):
        nationality = ''
        if 'nationality' in self.selector_map:
                nationality = self.process_xpath(response, self.get_selector_map('nationality')).get()
                if nationality:
                    nationality = re.sub('<[^<]+?>', '', nationality).strip().title()
        return nationality

    def get_ethnicity(self, response):
        ethnicity = ''
        if 'ethnicity' in self.selector_map:
                ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
                if ethnicity:
                    ethnicity = re.sub('<[^<]+?>', '', ethnicity).strip().title()
        return ethnicity

    def get_tattoos(self, response):
        tattoos = ''
        if 'tattoos' in self.selector_map:
            tattoo = self.process_xpath(response, self.get_selector_map('tattoos')).get()
            if tattoo:
                if "tattoo" in tattoo.lower():
                    tattoos = "Yes"
        return tattoos

    def get_piercings(self, response):
        piercings = ''
        if 'piercings' in self.selector_map:
            piercing = self.process_xpath(response, self.get_selector_map('piercings')).get()
            if piercing:
                if "piercing" in piercing.lower():
                    piercings = "Yes"
        return piercings

    def get_url(self, response):
        url = re.search('(.*)\\?nats',response.url).group(1)
        return url
