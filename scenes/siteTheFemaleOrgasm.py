import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheFemaleOrgasmSpider(BaseSceneScraper):
    name = 'TheFemaleOrgasm'
    network = 'The-Female-Orgasm'
    parent = 'The-Female-Orgasm'
    site = 'The-Female-Orgasm'

    start_urls = [
        'https://www.the-female-orgasm.com',
    ]

    selector_map = {
        'title': '//title/text()',
        're_title': r'(.*?) - ',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="model_update_block_image"]//img/@src0_2x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*)\.htm',
        'pagination': '/explore/categories/Movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            title = scene.xpath('./div[@class="updateInfo"]/h5/a/text()')
            if title:
                meta['title'] = title.get().strip()
            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace('.com/content', '.com/explore/content')
        return image
