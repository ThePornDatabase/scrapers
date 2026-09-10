import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBreedItRawSpider(BaseSceneScraper):
    name = 'BreedItRaw'
    network = 'Breed It Raw'
    parent = 'Breed It Raw'
    site = 'Breed It Raw'

    start_urls = [
        'https://breeditraw.net',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/p//text()',
        'image': '//script[contains(text(), "poster=")]/text()',
        're_image': r'poster=[\'\"](.*?)[\'\"]',
        'performers': '//div[contains(@class, "featuring")]/ul/li[contains(@class, "models")]/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class,"item-video")]')
        for scene in scenes:
            sceneid = scene.xpath('.//img[contains(@id, "set-target")]/@id').get()
            meta['id'] = re.search(r'-(\d+)', sceneid).group(1)

            scenedate = scene.xpath('.//div[@class="date"]/text()')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get())
                if scenedate:
                    meta['date'] = scenedate.group(1)

            scene_url = scene.xpath('.//div[1]/a/@href').get()

            if meta['id']:
                if self.check_item(meta, self.days):
                    yield scrapy.Request(url=self.format_link(response, scene_url), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//p[contains(text(), "of video")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "").replace(" ", "").strip().lower()
            duration = re.search(r'(\d+)ofvideo', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_tags(self, response):
        return ['Gay']