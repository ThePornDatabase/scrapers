import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJOIBabesSpider(BaseSceneScraper):
    name = 'JOIBabes'
    network = 'JOIBabes'
    parent = 'JOIBabes'
    site = 'JOIBabes'

    start_urls = [
        'https://joibabes.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//span[@class="dark:text-neutral-300"]/text()',
        'date': '//h1/following-sibling::div[1]//span[@class="block" and contains(text(), ",")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"gap-y-3")]//span[contains(text(), "Models")]/following-sibling::div/a/div/span/text()',
        'tags': '//div[contains(@class,"gap-y-3")]//span[contains(text(), "Categories")]/following-sibling::div/a/div/span/text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "bg-content1")]/a')
        for scene in scenes:
            duration = scene.xpath('.//span[contains(@class, "semibold")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())

            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
