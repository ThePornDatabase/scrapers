import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEroticDesireSpider(BaseSceneScraper):
    name = 'EroticDesire'
    site = 'Erotic Desire'
    parent = 'Erotic Desire'
    network = 'Erotic Desire'

    start_urls = [
        'https://eroticdesire.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h1/following-sibling::p[1]/text()',
        'tags': '//ul[contains(@class, "tags")]/li/a/text()',
        'external_id': r'.*/(.*?)/',
        'pagination': '/videos/latest?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "card_video")]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[contains(@class, "date")]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            meta['performers'] = scene.xpath('.//a[contains(@class, "model")]/text()').getall()
            meta['duration'] = self.duration_to_seconds(scene.xpath('.//span[contains(@class, "amount")]/text()').get())
            meta['image'] = scene.xpath('.//img/@src').get()
            meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
