import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VrAllureSpider(BaseSceneScraper):
    name = 'Karups'
    network = "Karups"

    start_urls = [
        'https://www.karups.com/'
    ]

    selector_map = {
        'title': '//span[@class="title"]/text()',
        'description': '',
        'date': '//span[@class="date"]/span[@class="content"]/text()',
        'image': '//video/@poster',
        'performers': '//span[@class="models"]/span[@class="content"]/a/text()',
        'tags': '',
        'trailer': '//video//source/@src',
        'external_id': '(\\d*).html$',
        'pagination': '/videos/page%s.html'
    }

    def get_scenes(self, response):

        scenes = response.xpath('//div[@class="item-inside"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        return ''

    def get_site(self, response):
        site = response.xpath(
            '//span[@class="sup-title"]/span[contains(@class,"site")]/text()').get()

        if site:
            site = site.strip()
            return site
        return ''

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()

        if not image:
            image = response.xpath(
                '//div[@class="video-poster"]/img/@src').get()

        if image:
            return self.format_link(response, image)
        return ''
