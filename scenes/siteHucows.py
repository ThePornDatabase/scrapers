import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class HucowsSpider(BaseSceneScraper):
    name = 'Hucows'
    network = 'Hucows'
    parent = 'Hucows'

    start_urls = [
        'https://www.hucows.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="entry-content"]//p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="posttags"]/a/text()',
        'tags': '//span[@class="postedintop"]/a/text()',
        'external_id': '\\/\\d+\\/\\d+\\/(.*)',
        'trailer': '',
        'pagination': '/category/updates/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//article/header/a/@href").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        sceneid = search.group(1).replace("/", "")
        return sceneid
