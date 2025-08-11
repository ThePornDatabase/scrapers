import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePOVClubSpider(BaseSceneScraper):
    name = 'ThePOVClub'
    network = 'ThePOVClub'
    parent = 'ThePOVClub'
    site = 'ThePOVClub'

    start_urls = [
        'https://thepovclub.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/h3/following-sibling::p//text()',
        'performers': '//li[contains(text(), "Featuring")]/following-sibling::li/a/text()',
        'tags': '//li[contains(text(), "Tags")]/following-sibling::li/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            image = scene.xpath('.//video/@poster')
            if image:
                image = self.format_link(response, image.get())
                meta['image'] = image.replace("-1x", "-4x")
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                if not meta['image_blob']:
                    meta['image_blob'] = self.get_image_blob_from_link(image)
                meta['id'] = re.search(r'.*/(\d+)-', image).group(1)
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"videoInfo")]/p/text()[contains(., "of video")]')
        if duration:
            duration = re.sub(r'[^a-z0-9]', "", duration.get().replace("&nbsp;", "").lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
