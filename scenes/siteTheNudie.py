import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheNudieSpider(BaseSceneScraper):
    name = 'TheNudie'
    network = 'The Nudie'

    start_urls = [
        'https://www.thenudie.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(text(), "Description")]/following-sibling::div/text()',
        'date': '',
        'image': '//div[contains(@class,"w-full")]//@poster-url',
        'performers': '//div[contains(text(), "Starring")]/following-sibling::div/span/div/text()',
        'tags': '//div[contains(text(), "Categories")]/following-sibling::div/span/a/text()',
        'external_id': r'.*/(.*?)$',
        'trailer': '',
        'pagination': '/scenes?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"w-full")]/a/@href').getall()
        for scene in scenes:
            scene = scene.strip()
            if re.search(self.get_selector_map('external_id'), scene) and "signup" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "The Nudie"

    def get_parent(self, response):
        return "The Nudie"
