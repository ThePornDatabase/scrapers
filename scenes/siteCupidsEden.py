import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCupidsEdenSpider(BaseSceneScraper):
    name = 'CupidsEden'
    network = 'CupidsEden'
    parent = 'CupidsEden'
    site = 'CupidsEden'

    start_urls = [
        'https://cupidseden.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="video-text"]/div/p/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-text"]//span[contains(text(), "Model:")]/following-sibling::text()',
        'tags': '//div[@class="video-text"]//span[contains(text(), "Tags:")]/following-sibling::a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/page%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//span[contains(@class, "title-info")]/..')
        for scene in scenes:
            image = scene.xpath('.//img/@src')
            if image:
                image = image.get()
                image = self.format_link(response, image)
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)

            scene = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
