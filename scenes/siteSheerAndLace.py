import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSheerAndLaceSpider(BaseSceneScraper):
    name = 'SheerAndLace'
    network = 'SheerAndLace'
    parent = 'SheerAndLace'
    site = 'SheerAndLace'

    start_urls = [
        'https://sheerandlace.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//h4[contains(text(), "description")]/following-sibling::p//text()',
        'date': '//span[contains(text(), "Added")]/following-sibling::text()[1]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'duration': '//p[contains(text(), "min") and contains(text(), "of video")]/text()',
        'tags': '//li[contains(@class, "label") and contains(text(), "Tags")]/following-sibling::li/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            meta['id'] = re.search(r'b(\d+)_', sceneid).group(1)
            scene = scene.xpath('./a/@href').get()
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

    def get_image(self, response):
        image = super().get_image(response)
        if "-1x" in image:
            image = image.replace("-1x", "-4x")
        return image
