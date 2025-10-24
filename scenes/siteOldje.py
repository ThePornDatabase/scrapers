import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOldjeSpider(BaseSceneScraper):
    name = 'Oldje'
    network = 'Oldje'
    parent = 'Oldje'
    site = 'Oldje'

    start_urls = [
        'https://www.oldje.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()|//h1[@class="preview_header"]/span[1]/text()',
        'description': '//div[@id="content"]//p[@class="text"]/text()|//div[@class="preview_desc"]/text()',
        'date': '//p[contains(text(), "Published")]/span/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//div[@id="content"]/a[1]/img/@src|//div[@class="content left"]/div/div[1]/a/img[contains(@src, "sets")]/@src',
        'performers': '//span[contains(@class,"act_name")]/a/text()',
        'tags': '//p[@class="tags"]/span/a/text()|//p[contains(@id, "tags")]/span/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/movies/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="left mini_cover"]/h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        return self.get_date(response)
