import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCherokeeDAssSpider(BaseSceneScraper):
    name = 'CherokeeDAss'
    site = 'Cherokee DAss'
    parent = 'Cherokee DAss'
    network = 'Cherokee DAss'

    start_urls = [
        'https://cherokeedass.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block"]//span[@class="update_title"]/text()',
        'description': '//div[@class="update_block"]//span[contains(@class,"update_description")]/text()',
        'date': '//div[@class="update_block"]//span[contains(@class,"update_date")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_block"]//div[@class="update_image"]/a[1]/@href',
        'performers': '//div[@class="update_block"]//span[contains(@class,"update_models")]/a/text()',
        'tags': '//div[@class="update_block"]//span[contains(@class,"update_tags")]/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/updates_%s_d.html',
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
        if ".com/content" in image:
            image = image.replace(".com/content", ".com/tour/content")
        if ".com/tour/content" not in image:
            image = response.xpath('//div[@class="update_image"]/a/img/@src0_3x')
            if image:
                image = "https://cherokeedass.com/tour" + image.get()
        return image

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_block_footer"]//div[contains(@class,"update_counts")]/text()')
        if duration:
            duration = re.sub(r'[^a-z0-9]+', '', duration.get().lower())
            if "min" in duration:
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    return str(int(duration.group(1)) * 60)
        return None
