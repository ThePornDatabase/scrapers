import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePerfectDSpider(BaseSceneScraper):
    name = 'PerfectD'
    network = 'PerfectD'
    parent = 'PerfectD'
    site = 'PerfectD'

    start_urls = [
        'https://perfectd.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "head-lg")]/text()',
        'image': '//div[contains(@class,"video-player")]//img/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/page%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video-card"]/div')
        for scene in scenes:
            image = scene.xpath('./a/img/@src')
            if image:
                meta['origimage'] = self.format_link(response, image.get())

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = response.xpath('//meta[@name="keywords"]/@content').get()
        tags = list(map(lambda x: string.capwords(x.strip()), tags.split(",")))
        for tag in tags.copy():
            title = self.get_title(response)
            if title.lower() in tag.lower():
                tags.remove(tag)
        if "Perfectd" in tags:
            tags.remove("Perfectd")
        return tags

    def get_image(self, response, path=None):
        meta = response.meta
        image = super().get_image(response)
        if ".jpg" not in image and ".png" not in image:
            image = meta['origimage']
        return image
