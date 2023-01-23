import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSwingingBiCouplesSpider(BaseSceneScraper):
    name = 'SwingingBiCouples'
    network = 'Swinging Bi Couples'
    parent = 'Swinging Bi Couples'
    site = 'Swinging Bi Couples'

    start_urls = [
        'https://www.swingingbicouples.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//img[contains(@class, "large_update_thumb ")]/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/tour/categories/updates_%s_p.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if "content" in image:
            image = image.replace(".com/content", ".com/tour/content")
        return image
