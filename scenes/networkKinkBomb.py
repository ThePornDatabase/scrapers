import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkKinkBombSpider(BaseSceneScraper):
    name = 'KinkBomb'
    network = 'KinkBomb'
    parent = 'KinkBomb'
    site = 'KinkBomb'

    start_urls = [
        'http://www.kinkbomb.com',
    ]

    selector_map = {
        'title': '//h1[@class="productviewtitle"]/text()',
        'description': '//div[@class="description-inner"]/p/text()',
        'date': '//span[contains(text(), "Posted:")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="clip-preview-inner"]/video/@poster',
        'performers': '',
        'tags': '//span[contains(text(), "categories")]/following-sibling::a/text()|//span[contains(text(), "Category")]/following-sibling::a/text()',
        'external_id': r'.*/(\d+)',
        'trailer': '//div[@class="clip-preview-inner"]/video/source/@src',
        'pagination': '/all?sort=age&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item card"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        site = response.xpath('//h4[@class="studio-header-name"]/text()')
        if site:
            site = site.get()
            title = string.capwords(site.strip()) + ": " + title
        return title
