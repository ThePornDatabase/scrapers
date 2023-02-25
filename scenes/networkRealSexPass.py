import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkRealSexPassSpider(BaseSceneScraper):
    name = 'RealSexPass'
    network = 'Real Sex Pass'

    start_urls = [
        'https://www.realsexpass.com',
    ]

    selector_map = {
        'title': '//h1[@class="heading cf"]/span/text()',
        'description': '//div[contains(@class,"video-info-desc")]/p/text()',
        'date': '',
        'image': '',
        'performers': '//div[@class="models"]//a/strong/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'duration': '//span[@class="time"]/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item"]')
        for scene in scenes:
            site = scene.xpath('.//span[contains(@class, "meta channel")]/text()')
            if site:
                meta['site'] = site.get().strip()
                meta['parent'] = site.get().strip()
            duration = scene.xpath('.//span[contains(@class, "meta time")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())
            image = scene.xpath('.//img/@src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            meta['trailer'] = scene.xpath('./@data-video').get()
            sceneid = scene.xpath('.//a/@href')
            meta['id'] = None
            if sceneid:
                sceneid = sceneid.get()
                sceneid = re.search(r'id=(\d+)', sceneid)
                if sceneid:
                    meta['id'] = sceneid.group(1)
                    scene = f"https://www.realsexpass.com/video/video-{meta['id']}.html"
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
