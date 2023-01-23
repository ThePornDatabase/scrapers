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

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        "MEDIA_ALLOW_REDIRECTS": True,
    }

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
