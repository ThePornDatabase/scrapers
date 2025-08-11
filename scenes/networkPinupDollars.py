import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPinupDollarsSpider(BaseSceneScraper):
    name = 'PinupDollars'
    network = 'Pinup Dollars'
    parent = 'Pinup Dollars'

    start_urls = [
        # ~ 'https://www.demmyblaze.com',
        # ~ 'https://www.lanakendrick.com',
        # ~ 'https://www.leannecrow.com',
        # ~ 'https://www.monicamendez.com',
        'https://www.pinupfiles.com',
        # ~ 'https://www.rachelaldana.com',
        # ~ 'https://www.tessafowler.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::span/text()',
        'date': '//strong[contains(text(),"Added")]/following-sibling::text()',
        'image': '//div[contains(@class, "player-window")]/following-sibling::img[contains(@class, "update_thumb")]/@src0_1x',
        'performers': '//div[contains(@class, "models-list-thumbs")]//a[contains(@href, "/models/")]/span/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video playsinline src=\"(.*?)\"',
        'external_id': r'',
        'pagination': '/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-thumb"]/a')
        for scene in scenes:
            meta['id'] = scene.xpath('./img/@id').get()
            meta['id'] = re.search(r'target-(\d+)', meta['id']).group(1)
            scene = scene.xpath('./@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        if performers:
            return performers
        if "demmyblaze" in response.url:
            return ["Demmy Blaze"]
        if "lanakendrick" in response.url:
            return ["Lana Kendrick"]
        if "leannecrow" in response.url:
            return ["Leanne Crow"]
        if "monicamendez" in response.url:
            return ["Monica Mendez"]
        if "rachelaldana" in response.url:
            return ["Rachel Aldana"]
        if "tessafowler" in response.url:
            return ["Tessa Fowler"]

    def get_tags(self, response):
        tags = super().get_tags(response)
        if tags:
            return tags
        return ['Huge Boobs']

    def get_image(self, response):
        image = super().get_image(response)
        print(response.url, image)
        return image
