import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLesbianSexualitySpider(BaseSceneScraper):
    name = 'LesbianSexuality'
    network = 'Lesbian Sexuality'
    parent = 'Lesbian Sexuality'
    site = 'Lesbian Sexuality'

    start_urls = [
        'https://lesbiansexuality.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class, "description")]/text()',
        'date': '',
        'image': '//div[@class="update_image"]/a/img/@src0_2x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        're_trailer': r'tload\(\'(.*\.mp4)',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            scenedate = scene.xpath('./div/p/span[contains(text(), "/20")]/text()').get()
            if scenedate:
                meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            else:
                meta['date'] = self.parse_date('today').isoformat()

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
