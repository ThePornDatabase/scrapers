import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteButchDixonSpider(BaseSceneScraper):
    name = 'ButchDixon'
    network = 'ButchDixon'
    parent = 'ButchDixon'
    site = 'ButchDixon'

    start_urls = [
        'https://www.butchdixon.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videonewinfo")]/h2/text()',
        'description': '//div[contains(@class, "container bloc")]//div[contains(@class, "videonewinfo")]/p/text()',
        'image': '//script[contains(text(), "jwplayer")]/text()',
        're_image': r'image\:.*?[\'\"](.*?)[\'\"]',
        'external_id': r'lid=(\d+)',
        'pagination': '/tour/show.php?a=744_%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="itemv"]')
        for scene in scenes:
            image = scene.xpath('.//img/@src')
            if image:
                meta['orig_image'] = f"https://www.butchdixon.com/tour/{image.get()}"

            scene = scene.xpath('./a/@href').get()
            scene = f"https://www.butchdixon.com/tour/{scene}"
            meta['id'] = re.search(r'lid=(\d+)', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace("com/preview", "com/tour/preview")
        return image

    def get_image_blob(self, response):
        if 'image_blob' not in self.get_selector_map():
            image = self.get_image(response)
            image_blob = self.get_image_blob_from_link(image)
            if not image_blob:
                image_blob = self.get_image_blob_from_link(response.meta['orig_image'])
            return image_blob
        return None

    def get_performers(self, response):
        title = super().get_title(response)
        title = title.lower().replace(" and ", "&").replace(", ", "&")
        if "&" in title:
            performers = title.split("&")
            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []
