import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteErickPlaySpider(BaseSceneScraper):
    name = 'ErickPlay'
    network = 'ErickPlay'
    parent = 'ErickPlay'
    site = 'ErickPlay'

    start_urls = [
        'https://erickplay.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'external_id': r'',
        'pagination': '/videos/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "col-md-4")]')
        for scene in scenes:
            duration = scene.xpath('.//span[contains(@class, "duration")]/text()')
            if duration:
                duration = duration.get()
                minutes = re.search(r'(\d+)m', duration)
                seconds = re.search(r'(\d+)s', duration)
                if minutes:
                    minutes = int(minutes.group(1)) * 60
                else:
                    minutes = 0
                if seconds:
                    seconds = int(seconds.group(1))
                else:
                    seconds = 0
                meta['duration'] = str(minutes + seconds)

            scene = scene.xpath('./a/@href').get()
            if scene:
                meta['id'] = re.search(r'.*/(.*?)$', scene)
                if meta['id']:
                    meta['id'] = meta['id'].group(1)
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ["Gay"]
