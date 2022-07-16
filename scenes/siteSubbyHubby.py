import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSubbyHubbySpider(BaseSceneScraper):
    name = 'SubbyHubby'
    network = 'Subby Hubby'
    parent = 'Subby Hubby'
    site = 'Subby Hubby'

    start_urls = [
        'https://www.subbyhubby.com',
    ]

    selector_map = {
        'title': '//div[@class="trailer-info"]//h1/text()',
        'description': '//p[@class="description"]/text()',
        'date': '//strong[contains(text(), "Release date:")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '',
        'performers': '//span[@class="models_list"]/ul/li//a/span/text()',
        'tags': '//span[@class="categories"]/ul/li/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*)\.html',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//span[@class="item-thumb"]/a')
        for scene in scenes:
            image = scene.xpath('./img/@src0_2x')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            else:
                meta['image'] = None
                meta['image_blob'] = None
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
