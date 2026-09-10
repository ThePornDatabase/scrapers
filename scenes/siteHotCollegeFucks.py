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
