import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHotCollegeFucksSpider(BaseSceneScraper):
    name = 'HotCollegeFucks'
    network = 'Hot College Fucks'
    parent = 'Hot College Fucks'
    site = 'Hot College Fucks'

    start_urls = [
        'https://hotcollegefucks.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h4[contains(text(), "description")]/following-sibling::p//text()',
        'date': '//span[contains(text(), "Added")]/following-sibling::text()[1]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="player-thumb"]//img/@src0_1x',
        'performers': '//h5/following-sibling::ul/li/a/text()',
        'duration': '//span[contains(text(), "Added")]/following-sibling::text()[contains(., "in")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            meta['id'] = re.search(r'b(\d+)_', sceneid).group(1)
            scene = scene.xpath('./a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
