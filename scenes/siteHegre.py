import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHegreSpider(BaseSceneScraper):
    name = 'Hegre'
    network = 'Hegre'
    parent = 'Hegre'
    site = 'Hegre'

    start_urls = [
        'https://www.hegre.com',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//div[contains(@class,"record-description")]/div/p//text()',
        'date': '//div[contains(@class,"date-and-covers")]/span/text()',
        'image': '//div[contains(@class,"video-player-wrapper")]/@style',
        're_image': r'(http.*\.jpg)',
        'performers': '//div[contains(@class,"record-models")]/a/@title',
        'tags': '//div[contains(@class,"current-tags")]/div/a/text()',
        'external_id': r'.*/(.*?)$',
        'trailer': '//video/source[contains(@type,"mp4")]/@src',
        're_trailer': r'(.*)\?',
        'pagination': '/movies?films_sort=most_recent&films_page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
