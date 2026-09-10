import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClubStilettoSpider(BaseSceneScraper):
    name = 'ClubStiletto'
    network = 'ClubStiletto'
    parent = 'ClubStiletto'
    site = 'ClubStiletto'

    start_urls = [
        'https://www.clubstiletto.com',
    ]

    selector_map = {
        'title': '//h1[@class="page-header"]/text()',
        'description': '//div[contains(@class, "text-with-summary")]//div[contains(@class,"field-item even")]//text()',
        'date': '//div[contains(@class, "field-type-ds")]//div[contains(@class,"field-item even")]//text()[contains(., " - ") and contains(., ":")]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'performers': '//div[contains(@class, "field-type-entityreference")]//div[contains(@class,"field-item even")]/a/text()',
        'tags': '',
        'duration': '//div[contains(@class, "field-type-ds")]//div[contains(@class,"field-item even")]//text()[contains(., " - ") and contains(., ":")]',
        're_duration': r'(\d{1,2}:\d{2})',
        'external_id': r'.*/(.*?)$',
        'pagination': '/video_pages?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "views-field-title")]')
        for scene in scenes:

            image = scene.xpath('./ancestor::div[1]//img[contains(@class, "responsive") and contains(@src, ".png")]/@src')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])


            scene_url = scene.xpath('./span[1]/a[1]/@href')
            meta['url'] = self.format_link(response, scene_url.get())
            if meta['url']:
                yield scrapy.Request(url=meta['url'], callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['BDSM', 'Dominatrix', 'Femdom']

    def get_id(self, response):
        orig_id = super().get_id(response)
        external_id = response.xpath('//link[@rel="shortlink"]/@href').get()
        if external_id:
            external_id = re.search(r'node/(\d+)', external_id)
            if external_id:
                return external_id.group(1)
        return orig_id
