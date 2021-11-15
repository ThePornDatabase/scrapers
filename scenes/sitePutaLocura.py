import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PutaLocuraSpider(BaseSceneScraper):
    name = 'PutaLocura'
    network = 'Puta Locura'
    parent = 'Puta Locura'
    site = 'Puta Locura'

    start_urls = [
        'https://www.putalocura.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[@class="description clearfix"]/p[2]/text()',
        'date': '//div[@class="released-views"]/span[1]/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//script[contains(text(), "fluidPlayer")]/text()',
        're_image': r'posterImage: ?\"(.*?)\"',
        'performers': '',  # They can be pulled with '//span[@class="site-name"]/text()', but halfway through the same spot becomes sites or categories instead
        'tags': '',
        'external_id': r'.*\/(.*?)$',
        'trailer': '',
        'pagination': '/en?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="girls-site-box"]/var/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if "|" in title:
            title = re.search(r'(.*)\|', title).group(1)
        if title:
            return self.cleanup_title(title)
        return ''

    def get_performers(self, response):
        return []

    def get_tags(self, response):
        return ["Spanish"]
