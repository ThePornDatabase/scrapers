import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClubFillySpider(BaseSceneScraper):
    name = 'ClubFilly'
    network = 'Club Filly'

    start_urls = [
        'http://www.clubfilly.com',
    ]

    selector_map = {
        'title': '//div[@class="fltWrap"]/h1/span/text()',
        'description': '//p[@class="description"]/text()',
        'date': '//div[contains(text(), "Release Date")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//ul[@id="lstSceneFocus"]/li/img/@src',
        'performers': '//p[@class="starring"]/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'vnum=(\w\d+)',
        'trailer': '',
        'pagination': '/scenes.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//td[@class="ttlScene"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Club Filly"

    def get_parent(self, response):
        return "Club Filly"

    def get_performers(self, response):
        performers = response.xpath(self.get_selector_map('performers'))
        if performers:
            performers = performers.get()
            if "," in performers:
                performers = performers.split(",")
                return list(map(lambda x: string.capwords(x.strip()), performers))

    def get_tags(self, response):
        return ['Lesbian']
