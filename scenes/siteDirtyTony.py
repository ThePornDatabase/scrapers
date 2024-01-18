import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDirtyTonySpider(BaseSceneScraper):
    name = 'DirtyTony'
    network = 'Dirty Tony'
    parent = 'Dirty Tony'
    site = 'Dirty Tony'

    start_urls = [
        'http://dirtytony.com',
    ]

    selector_map = {
        'title': '//div[contains(@id, "content-wrap")]/div[1]/div[1]/div[1]/h1/text()',
        'description': '//h5/text()',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'',
        'pagination': '/tour/?paged=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h1/@id').getall()
        for scene in scenes:
            meta['id'] = re.search(r'-(\d+)$', scene).group(1)
            scene = f"http://dirtytony.com/tour/?p={meta['id']}"
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//video/@poster')
        if image:
            image = image.get()
            image = image.replace("..", "")
            image = "http://dirtytony.com" + image
        return image

    def get_tags(self, response):
        return ['Gay']
