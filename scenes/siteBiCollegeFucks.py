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
        # div.videothumb (and the b<id>_ class the id came from) is gone; cards are
        # div.item-update now.  The still has to come off the card too -- the scene
        # page's set-target images are the related-scene strip, whose first entry is
        # a different scene.
        for card in response.xpath('//div[contains(@class, "item-update")]'):
            link = card.xpath('.//div[contains(@class, "item-thumb")]//a/@href').get()
            if not link:
                continue

            meta = dict(response.meta)
            sceneid = card.xpath('.//img/@id').get() or ''
            sceneid = re.search(r'set-target-(\d+)', sceneid)
            meta['id'] = sceneid.group(1) if sceneid else None

            image = card.xpath('.//img/@src0_1x').get()
            if image:
                meta['image'] = self.format_link(response, image)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        return response.meta.get('image', '')
