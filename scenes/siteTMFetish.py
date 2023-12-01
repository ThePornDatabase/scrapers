import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTMFetishSpider(BaseSceneScraper):
    name = 'TMFetish'
    network = 'TMFetish'
    parent = 'TMFetish'
    site = 'TMFetish'

    start_urls = [
        'https://tmfetish.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()[1]',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img/@src0_3x',
        'performers': '',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            performers = scene.xpath('.//span[contains(@class, "tour_update_models")]/a/text()')
            if performers:
                meta['performers'] = list(map(lambda x: string.capwords(x.strip()), performers.getall()))
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        scene_id = super().get_id(response)
        return scene_id.lower()

    def get_duration(self, response):
        duration = response.xpath('//span[@class="availdate"]//text()')
        if duration:
            duration = duration.getall()
            duration = " ".join(duration).lower()
            duration = re.search(r'(\d+)\s+?min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None

    def get_date(self, response):
        scene_date = response.xpath('//span[@class="availdate"]/text()[1]')
        if scene_date:
            scene_date = scene_date.getall()
            scene_date = " ".join(scene_date)
            scene_date = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scene_date)
            if scene_date:
                scene_date = self.parse_date(scene_date.group(1), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
                return scene_date
        return ''
