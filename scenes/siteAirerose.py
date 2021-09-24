import re
from datetime import date
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAireroseSpider(BaseSceneScraper):
    name = 'Airerose'
    network = 'Airerose'
    parent = 'Airerose'
    site = 'Airerose'

    start_urls = [
        'http://airerose.com/'
    ]

    max_pages = 10

    selector_map = {
        'title': '//div[@id="vidinfo"]/h2/text()',
        'performers': '//div[@id="vidinfo"]/p[contains(text(),"Pornstars")]/a/text()',
        'description': '//div[@id="vidinfo"]/p[1]/text()',
        'date': '',  # I hate it, but there is no date.  Use current date, hopefully will catch on import for new ones
        'image': '//div[@id="video_preview"]/a/img/@src',
        'tags': '//div[@id="vidinfo"]/p[contains(text(),"Tags")]/a/text()',
        'external_id': r'(\d+).html',
        'trailer': '',
        'pagination': '/videos/?page=%s&sort=mostrecent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumbnail"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'Airerose'})

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        if not search:
            search = re.search(r'videos\/(.*).html', response.url, re.IGNORECASE)
        return search.group(1)

    def get_date(self, response):
        return date.today().isoformat()
