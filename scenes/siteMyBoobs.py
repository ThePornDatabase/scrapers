import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MyBoobsSpider(BaseSceneScraper):
    name = 'MyBoobs'
    network = "Radical Entertainment"
    parent = "MyBoobs"

    start_urls = [
        'https://tour.myboobs.eu'
    ]

    selector_map = {
        'title': '//h2[@class="sec-tit"]/span/text()',
        'description': '',
        'date': '',
        'image': '//img[@id="preview"]/@src',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': 'view\\/(\\d+)\\/',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):

        scenes = response.xpath('//div[contains(@class,"set-thumb")]')
        for scene in scenes:
            date = scene.xpath('./div/div/div/span/span[1]/text()').get()
            date = self.parse_date(date.strip()).isoformat()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})
