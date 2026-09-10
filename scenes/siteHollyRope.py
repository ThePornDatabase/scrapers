import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHollyRopeSpider(BaseSceneScraper):
    name = 'HollyRope'
    network = 'HollyRope'
    parent = 'HollyRope'
    site = 'HollyRope'

    start_urls = [
        'https://hollyrope.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "videoDescription")]/p//text()',
        'date': '//h1/following-sibling::div/ul/li/i[contains(@class, "fa-calendar")]/following-sibling::text()',
        'image': '//div[contains(@class, "videoPreview")]//iframe/@src',
        'performers': '//div[contains(@class, "models")]/ul/li/a/text()',
        'tags': '//div[contains(@class, "tags")]/ul/li/a/text()',
        'duration': '//h1/following-sibling::div/ul/li/i[contains(@class, "fa-clock")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "videoPic")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = [t.lstrip("#") for t in tags]
        tags.extend(['Bondage'])
        return tags
    
    def get_image(self, response):
        image = super().get_image(response)
        if image and "=http" in image:
            image = re.search(r'=(http.*)', image).group(1)
        return image
    
    def get_id(self, response):
        orig_sceneid = super().get_id(response)
        scene_id = response.xpath('//div[@class="twoBtns"]/a/@id').get()
        if scene_id:
            scene_id = re.search(r'-(\d+)', scene_id).group(1)
            return scene_id
        return orig_sceneid
    
    def get_performers_data(self, response):
        performers = super().get_performers(response)
        perf_data = []
        for performer in performers:
            perf = {}
            perf['name'] = performer
            perf['url'] = f"https://hollyrope.com/models/{performer.replace(' ', '-').lower()}"
            perf['site'] = 'HollyRope'
            perf['network'] = 'HollyRope'
            perf['image'] = f"https://hollyrope.com/content/performer/{performer.replace(' ', '-').lower()}.jpg"
            perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
            perf['extra'] = {'gender': "Female"}
            perf_data.append(perf)
        return perf_data