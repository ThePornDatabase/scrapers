import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLatinBoyzSpider(BaseSceneScraper):
    name = 'LatinBoyz'
    site = 'LatinBoyz'
    parent = 'LatinBoyz'
    network = 'LatinBoyz'

    start_urls = [
        'https://latinboyz.com'
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '//div[@class="entry-content"]/p[1]/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/',
        'pagination': '/homepage%s/',
    }

    def get_next_page_url(self, base, page):
        print(page, base)
        if int(page) == 1:
            return base
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//header[contains(@class, "item-header")]')
        for scene in scenes:
            tags = scene.xpath('./following-sibling::footer/ul/li/a/text()')
            if tags:
                tags = tags.getall()
                meta['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))

            scene = scene.xpath('./figure/a/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
