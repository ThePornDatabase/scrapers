import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFitEroticSpider(BaseSceneScraper):
    name = 'FitErotic'
    network = 'FitErotic'
    parent = 'FitErotic'
    site = 'FitErotic'

    start_urls = [
        'https://fiterotic.com',
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '//figcaption[contains(@class,"wp-element-caption")]/text()',
        'date': '//time[contains(@class,"entry-date") and contains(@class, "published")]/@datetime',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//header[@class="entry-header"]/following-sibling::div[1]/div[@class="wp-block-image"]/figure[1]/a[1]/img[1]/@src[1]|//div[@class="entry-content"]//a/img/@src',
        'performers': '',
        'tags': '//footer[@class="entry-footer"]//a[contains(@href, "/category/")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/tour/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
