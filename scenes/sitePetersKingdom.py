import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePetersKingdomSpider(BaseSceneScraper):
    name = 'PetersKingdom'
    network = 'Peters Kingdom'
    parent = 'Peters Kingdom'
    site = 'Peters Kingdom'

    start_urls = [
        'https://peterskingdom.com',
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
                if image:
                    image = re.search(r'.*(http.*?768.*?\.(?:jpg|png))', image)
                if image:
                    meta['image'] = self.format_link(response, image.group(1))
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            if not image:
                image = scene.xpath('./img/@srcset').get()
                if image:
                    image = re.search(r'.*(http.*?750.*?\.(?:jpg|png))', image)
                if image:
                    meta['image'] = self.format_link(response, image.group(1))
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            if not image:
                image = scene.xpath('./img/@srcset').get()
                if image:
                    image = re.search(r'.*(http.*?360.*?\.(?:jpg|png))', image)
                if image:
                    meta['image'] = self.format_link(response, image.group(1))
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
