import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFutanaricaSpider(BaseSceneScraper):
    name = 'Futanarica'
    network = 'Futanarica'
    parent = 'Futanarica'
    site = 'Futanarica'

    start_urls = [
        'https://futanarica.com',
    ]

    selector_map = {
        'title': '//h3[@class="post_title entry-title"]/text()',
        'description': '//div[contains(@class, "post_content")]/p[1]/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//div[contains(@class, "post_content")]/a/img/@src',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)/$',
        'trailer': '//div[contains(@class, "post_content")]/a/@href',
        'pagination': '/releases/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        return ['3D CG', 'Animation', 'Hentai', 'Futanari']
