import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class SinematicaSpider(BaseSceneScraper):
    name = 'Sinematica'
    network = 'Sinematica'
    parent = 'Sinematica'

    start_urls = [
        'https://www.sinematica.com/'
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[@class="mediaMeta"]/h2/text()',
        'date': '//span[@class="posted_on"]/i[contains(@class, "calendar")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="feat"]/a/text()',
        'tags': "",
        'external_id': 'details\\/(\\d+)?',
        'trailer': '//video/source/@src',
        'pagination': '/search/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@id="_posts"]/div[@class="post_new"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
