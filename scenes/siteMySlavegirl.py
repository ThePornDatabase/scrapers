import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMySlavegirlSpider(BaseSceneScraper):
    name = 'MySlavegirl'
    network = 'My Slavegirl'
    parent = 'My Slavegirl'
    site = 'My Slavegirl'

    start_urls = [
        'https://www.my-slavegirl.com',
    ]

    selector_map = {
        'title': '//h1[@class="h2"]/text()',
        'description': '//div[@class="custom_text"]/p/text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': r'collections/(.*)',
        'trailer': '//meta[@name="twitter:player:stream"]/@content',
        're_trailer': r'(.*\.mp4)',
        'pagination': '/collections/page/%s'
    }

    def get_scenes(self, response):
        # The listing was restructured: each collection is now a div.collection
        # carrying its own title link, cast and runtime.
        for card in response.xpath('//div[contains(@class, "collection")][.//div[@class="title-block"]]'):
            scene = card.xpath('.//div[@class="title-block"]//h2/a/@href').get()
            if not scene or not re.search(self.get_selector_map('external_id'), scene):
                continue
            meta = {}
            runtime = card.xpath('.//span[contains(@class, "fa5-text")]/text()').re_first(r'(\d+):(\d+)\s*minutes')
            runtime = card.xpath('.//span[contains(@class, "fa5-text")]/text()').re_first(r'(\d+:\d+)\s*minutes')
            if runtime:
                meta['duration'] = self.duration_to_seconds(runtime)
            performers = card.xpath('.//span[contains(@class, "models")]//a/text()').getall()
            performers = [x.strip() for x in performers if x and x.strip()]
            if performers:
                meta['performers'] = performers
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
