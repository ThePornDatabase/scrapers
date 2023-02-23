import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class GasmSpider(BaseSceneScraper):
    name = 'Gasm'
    network = 'Gasm'
    parent = 'Gasm'

    start_urls = [
        'https://www.gasm.com/studio/profile/harmonyvision'
    ]

    selector_map = {
        'title': '//span[contains(@class,"gqTitle")]/text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"gqOwner")]/a/text()',
        'tags': './/a[contains(@class,"gqTag")]/text()',
        'duration': './/div[contains(@class,"gqMediaInfo")]/span[contains(@class,"gqText")]/text()',
        'trailer': '',
        'site': '//span[contains(@class,"gqOwner")]/a/text()',
        'external_id': r'details\/([0-9]+)',
        'pagination': '?page=%s',
        'type': 'Scene',
    }

    sites = {
        'harmonyvision': "HarmonyVision"
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="gqFeed"]')
        for scene in scenes:
            link = self.format_link(response, scene.xpath('.//a[contains(@class,"gqTop")]/@href').get())
            if re.search(self.get_selector_map('external_id'), link):
                meta = {}
                meta['tags'] = self.get_tags(scene)
                meta['duration'] = self.get_duration(scene)
                yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = self.get_element(response, 'site')
        return self.sites[site.lower()]

    def get_next_page_url(self, base, page):
        return base + self.get_selector_map('pagination') % page
