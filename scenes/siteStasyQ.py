import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteStasyQSpider(BaseSceneScraper):
    name = 'StasyQ'
    network = 'StasyQ'
    parent = 'StasyQ'
    site = 'StasyQ'

    start_urls = [
        'https://www.stasyq.com',
    ]

    cookies = []

    selector_map = {
        'title': '//meta[@itemprop="position" and @content="2"]/preceding-sibling::a[1]/span/text()',
        'description': '//div[contains(@class, "about-section")]/p//text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="release-card__model"]/p/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'(\d+)$',
        'pagination': '/releases?sort=recent&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[contains(text(), "All Releases")]//ancestor::section[1]//div[contains(@class,"release-preview-card__content")]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[contains(@class, "d-flex")]/div[contains(@class, "text-grey")][1]/p/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    meta['date'] = scenedate.group(1)

            scene = scene.xpath('.//h3/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Erotica']
