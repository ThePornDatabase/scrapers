import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSapphixSpider(BaseSceneScraper):
    name = 'Sapphix'
    network = 'Sapphix'
    parent = 'Sapphix'
    site = 'Sapphix'

    date_trash = ['Released:', 'Added:', 'Published:', 'Added']

    start_urls = [
        'https://www.sapphix.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//p[@class="mg-md"]/text()',
        'date': '//div[@class="row"]/div[contains(@class,"text-right")]/span/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@id="videoPlayer"]//video/@poster',
        'performers': '//h4[contains(text(), "Featured")]/following-sibling::p/a/text()',
        'tags': '//h4[contains(text(), "Tags")]/following-sibling::a/text()',
        'external_id': r'movies/(.*)/',
        'trailer': '//div[@id="videoPlayer"]//video/source/@src',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="itemm"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_url(self, response):
        url = re.search(r'(.*)\?nats', response.url)
        if url:
            url = url.group(1)
            return url.strip()
        return response.url
