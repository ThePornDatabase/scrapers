import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRestrictedSensesSpider(BaseSceneScraper):
    name = 'RestrictedSenses'
    network = 'Restricted Senses'

    start_urls = [
        'http://restrictedsenses.com',
    ]

    selector_map = {
        'title': '//article/h1/a/text()',
        'description': '//article/p[1]/text()',
        'date': '//span[@class="entry-date"]/text()',
        'image': '//div[@class="pin-container"]/img/@src',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': '/main/updates/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/h4/../h1/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Restricted Senses"

    def get_parent(self, response):
        return "Restricted Senses"

    def get_performers(self, response):
        description = response.xpath('//article/p[1]/text()')
        if description:
            description = description.get()
            if "Mina" in description:
                return ['Mina']
        return []

    def get_tags(self, response):
        return ['Bondage', 'Fetish']
