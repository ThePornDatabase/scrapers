import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackPaybackSpider(BaseSceneScraper):
    name = 'BlackPayback'
    network = 'Black Payback'
    parent = 'Black Payback'
    site = 'Black Payback'
    max_pages = 15

    start_urls = [
        'https://blackpayback.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '',
        'image': '//script[contains(text(),"video_content")]/text()',
        're_image': r'poster=\"(.*?\.jpg)',
        'performers': '',
        'tags': '//div[contains(@class,"featuring")]/ul/li/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene) and response.meta['page'] < self.max_pages:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
