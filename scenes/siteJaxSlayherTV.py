import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJaxSlayherTVSpider(BaseSceneScraper):
    name = 'JaxSlayherTV'
    network = 'JaxSlayherTV'
    parent = 'JaxSlayherTV'
    site = 'JaxSlayherTV'

    start_urls = [
        'https://jaxslayher.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/text()',
        'description': '',
        'date': '//ul[@class="statistic_list"]/li[@class="item"][2]/span/text()',
        'date_formats': ['%b %s/%Y'],
        'performers': '//div[@class="detail_info"]/div[@class="actor"]//a/text()',
        'tags': '',
        'duration': '//ul[@class="statistic_list"]/li[@class="item"][1]/span/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/tour/videos/most-recent/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid_item"]')
        for scene in scenes:
            image = scene.xpath('.//picture/source[1]/@srcset').get()
            if image:
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            else:
                meta['image'] = ''
                meta['image_blob'] = ''
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and "join" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
