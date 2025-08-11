import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteBiCollegeFucksSpider(BaseSceneScraper):
    name = 'BiCollegeFucks'
    network = 'BiCollegeFucks'
    parent = 'BiCollegeFucks'
    site = 'BiCollegeFucks'

    cookies = [{"name": "warn", "value": "true"}]

    start_urls = [
        'https://bicollegefucks.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="description"]/p//text()',
        'date': '//span[contains(text(), "Added:")]/following-sibling::text()[contains(., ",")]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//img[contains(@id, "set-target")]/@src0_1x',
        'performers': '//div[contains(@class, "modelFeaturing")]/ul/li/a/text()',
        'duration': '//div[@class="player-time"]/text()',
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
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
