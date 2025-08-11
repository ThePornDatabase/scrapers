import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFetishProsSpider(BaseSceneScraper):
    name = 'FetishPros'
    network = 'Fetish Pros'
    parent = 'Fetish Pros'
    site = 'Fetish Pros'

    start_urls = [
        'https://www.fetishpros.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="contentD"]//div[contains(@class, "videoDescription")]//span/text()',
        'date': '//div[@class="contentD"]//i[contains(@class, "calendar")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@class="contentD"]//div[contains(@class, "videoPreLeft")]//iframe/@src',
        're_image': r'poster=(http.*)',
        'performers': '//div[@class="contentD"]//div[contains(@class, "models")]/ul/li/a/text()',
        'tags': '//div[@class="contentD"]//div[contains(@class, "tags")]/ul/li/a/text()',
        'duration': '//div[@class="contentD"]//i[contains(@class, "clock")]/following-sibling::text()',
        'external_id': r'.*/(.*?)$',
        'trailer': '',
        'pagination': '/updates?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoPic"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
