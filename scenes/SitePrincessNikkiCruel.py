import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePrincessNikkiCruelSpider(BaseSceneScraper):
    name = 'PrincessNikkiCruel'
    network = 'Princess Nikki Cruel'
    parent = 'Princess Nikki Cruel'
    site = 'Princess Nikki Cruel'

    start_urls = [
        'https://shop.princessnikkicruel.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "collection-details")]/div[1]/pre//text()',
        'date': '//i[contains(@class, "calendar")]/following-sibling::span[1]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//i[contains(@class, "fa-tags")]/following-sibling::span[1]/a/text()',
        'duration': '//i[contains(@class, "image")]/following-sibling::span[1]/text()[contains(., "inutes")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': r'',
        'pagination': '/collections/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="collection"]')
        for scene in scenes:
            sceneid = scene.xpath('./@id').get()
            meta['id'] = re.search(r'_(\d+)', sceneid).group(1)
            scene = scene.xpath('./div[1]/h2/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, reponse):
        return ['Princess Nikki']
