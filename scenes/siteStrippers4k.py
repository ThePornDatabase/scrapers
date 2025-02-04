import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStrippers4kSpider(BaseSceneScraper):
    name = 'Strippers4k'
    network = 'PornPros'
    parent = 'Strippers4k'
    site = 'Strippers4k'

    start_urls = [
        'https://strippers4k.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "scene-info")]/div[contains(@class, "items-start")]/span/text()',
        'image': '//div[@data-controller="player"]//video/@poster',
        'performers': '//div[contains(@class, "scene-info")]//a[contains(@href, "/models/")]/text()',
        'external_id': r'',
        'pagination': '/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-thumbnail")]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[contains(@class, "-footer")]//span[contains(@class, "text-xs")]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            meta['id'] = scene.xpath('./@data-vid').get()
            scene = scene.xpath('./div[1]/div[1]/a[contains(@href, "/video/")]/@href').get()

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
