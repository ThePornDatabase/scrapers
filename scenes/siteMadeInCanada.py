import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MadeInCanadaSpider(BaseSceneScraper):
    name = 'MadeInCanada'
    network = "Radical Entertainment"
    parent = "MadeInCanada"

    start_urls = [
        'http://tour.madeincanada.xxx/'
    ]

    selector_map = {
        'title': '//h2[@class="sec-tit"]/span/text()',
        'description': '//div[@class="preview-description"]/p/text()',
        'date': '//div[@class="released-date"]/span[@class="grey"]/text()',
        'image': '//a[@id="fake-play"]/div[contains(@class,"preview-container")]/img/@src',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': '\\/view\\/(\\d*)\\/',
        'pagination': '/scenes?page=%s'
    }

    def get_scenes(self, response):

        scenes = response.xpath(
            '//div[contains(@class,"set-thumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = self.process_xpath(
            response, self.get_selector_map('description')).get()

        if description is not None:
            return self.cleanup_description(re.sub('<[^<]+?>', '', description.strip()))
        return ""

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if "-0001" in date:
            date = date.replace("-0001", "2014")
        date.replace('Released:', '').replace('Added:', '').strip()
        return self.parse_date(date.strip()).isoformat()
