import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteForplayFilmsSpider(BaseSceneScraper):
    name = 'ForplayFilms'
    network = 'ForplayFilms'
    parent = 'ForplayFilms'
    site = 'ForplayFilms'

    start_urls = [
        'https://forplayfilms.com/videos/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2[contains(text(), "DESCRIPTION")]/following-sibling::p/span/text()',
        'date': '//script[@class="yoast-schema-graph"]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[@class="post-tags"]/p/a/text()',
        'duration': '//p[contains(text(), "Runtime")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'video/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videos-poster"]//a[@class="lsexplore"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//p[contains(text(), "Performers")]/text()')
        if performers:
            performers = re.search(r': (.*)', performers.get()).group(1)
            return list(map(lambda x: string.capwords(x.strip()), performers.split(",")))
        return []
