import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkMadhotXSpider(BaseSceneScraper):
    name = 'MadhotX'
    network = 'MadhotX'

    start_urls = [
        'https://madhotx.com/videos/2',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//p[@class="desc"]/text()',
        'date': '',
        'image': '//video/@data-poster',
        're_image': r'(.*)\?',
        'performers': '',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*)',
        'pagination': '/videos/%s?order=latest',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item"]')
        for scene in scenes:
            site = scene.xpath('.//p[@class="project-episode"]/span[1]/text()').get()
            site = re.sub(r'[^a-zA-Z ]', '', site).strip()
            meta['site'] = site
            meta['parent'] = site
            duration = scene.xpath('.//span[contains(@class, "duration")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())
            scene = scene.xpath('./a[@class="gallery-item"]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
