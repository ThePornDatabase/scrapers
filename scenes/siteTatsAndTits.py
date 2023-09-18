import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTatsAndTitspider(BaseSceneScraper):
    name = 'TatsandTits'
    network = 'Tats and Tits'
    parent = 'Tats and Tits'
    site = 'Tats and Tits'

    start_urls = [
        'https://tatsandtits.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "vid-box")]/h1/text()',
        'description': '//div[contains(@class, "vid-box")]/p/text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '//div[contains(@class, "pscat")]/a/text()',
        'tags': '//div[contains(@class, "pscat")]/span/a/text()',
        'external_id': r'([A-Za-z0-9]+(-[A-Za-z0-9]+)+)',
        'trailer': '',
        'pagination': '/videos/page/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[@class="vid-listing"]/li')
        for scene in scenes:
            scenedate = scene.xpath('./div[@class="date"]/text()')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
            scene = self.format_link(response, scene.xpath('./a/@href').get())
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
