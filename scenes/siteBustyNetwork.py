import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBustyNetworkSpider(BaseSceneScraper):
    name = 'BustyNetwork'
    network = 'Busty Network'
    parent = 'Busty Network'
    site = 'Busty Network'

    start_urls = [
        'http://bustynetwork.com',
    ]

    selector_map = {
        'title': '//div[@id ="vidinfo"]/h2/text()',
        'description': '//div[@id ="vidinfo"]/p[not(contains(text(), "Pornstars:")) and not(contains(text(), "Tags:"))][1]/text()',
        'image': '//div[contains(@id, "video_preview")]//img[contains(@src, ".jpg")]/@src',
        'performers': '//div[@id ="vidinfo"]/p[contains(text(), "Pornstars:")]/a/text()',
        'tags': '//div[@id ="vidinfo"]/p[contains(text(), "Tags:")]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'[-_](\d+)\.htm',
        'pagination': '/videos/?page=%s&sort=mostrecent',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article')
        for scene in scenes:
            scenedate = scene.xpath('.//p[contains(text(), "Released")]/span/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
