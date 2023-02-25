import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHDVPassSpider(BaseSceneScraper):
    name = 'HDVPass'
    network = 'HDVPass'
    parent = 'HDVPass'
    site = 'HDVPass'

    start_urls = [
        'http://hdvpass.com',
    ]

    selector_map = {
        'title': '//div[@id="video"]/div/h2/text()',
        'description': '//div[@id="video"]/div/p[1]/text()',
        'date': '',
        'image': '//div[@id="video"]/div[contains(@id, "preview")]/img/@src',
        'performers': '//div[@id="video"]/div/p[contains(text(), "Pornstars:")]/a/text()',
        'tags': '//div[@id="video"]/div/p[contains(text(), "Tags:")]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'(\d+)\.htm',
        'pagination': '/videos/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li/a[contains(@class, "thumb-link")]')
        for scene in scenes:
            scenedate = scene.xpath('./following-sibling::span[2]/text()')
            if scenedate:
                scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate.get())
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%B %d, %Y']).isoformat()
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
