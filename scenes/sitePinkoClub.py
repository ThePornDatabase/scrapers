import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePinkoClubSpider(BaseSceneScraper):
    name = 'PinkoClub'
    network = 'Pinko Club'

    start_urls = [
        'https://www.pinkoclub.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h4/a/text()',
        'tags': '',
        'external_id': r'.*/(\d+.*?)\.php',
        'trailer': '',
        'pagination': '/new-video.php?next=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="contorno01"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Pinko Club"

    def get_parent(self, response):
        return "Pinko Club"

    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_tags(self, response):
        return []

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("\n", "").replace("\r", "").strip()
        return description
