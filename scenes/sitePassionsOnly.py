import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePassionsOnlySpider(BaseSceneScraper):
    name = 'PassionsOnly'
    network = 'Passions Only'
    parent = 'Passions Only'
    site = 'Passions Only'

    start_urls = [
        'https://www.passionsonly.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "video-details")]/div/h1/text()',
        'description': '//div[@class="post-entry"]/p/text()',
        'date': '',
        'image': '',
        'performers': '//span[@class="meta-info"]/following-sibling::a/text()',
        'tags': '',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'video/(.*)/',
        'pagination': '/videos/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article/div[1]/a[1]')
        for scene in scenes:
            image = scene.xpath('./img/@srcset')
            if image:
                image = scene.xpath('./img/@srcset').get()
                image = image.split(",")
                image = image[-1]
                image = re.search(r'.*(http.*?\.\w{3,4})\s', image).group(1)
                if image:
                    meta['image'] = image
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
