import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJustPOVSpider(BaseSceneScraper):
    name = 'JustPOV'
    site = 'JustPOV'
    parent = 'JustPOV'
    network = 'JustPOV'

    start_urls = [
        'https://www.justpov.com'
    ]

    selector_map = {
        'title': '//div[@class="update_block_info"]//span[@class="update_title"]/text()',
        'description': '//div[@class="update_block_info"]//span[@class="latest_update_description"]/text()',
        'date': '//div[@class="update_block_info"]//span[@class="availdate"]/text()',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img[contains(@src0_3x, "jpg")]/@src0_3x',
        'performers': '//div[@class="update_block_info"]/span[@class="tour_update_models"]/a/text()',
        'tags': '//div[@class="update_block_info"]/span[@class="update_tags"]/a/text()',
        'duration': '',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'[\'\"](.*?)[\'\"]',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/tour/categories/movies_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "updateItem")]')
        for scene in scenes:
            meta['id'] = scene.xpath('./a/img/@alt').get()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "")
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None

    def get_image(self, response):
        image = super().get_image(response)
        if ".com/content" in image:
            image = image.replace(".com/content", ".com/tour/content")
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        if ".com/trailers" in trailer:
            trailer = trailer.replace(".com/trailers", ".com/tour/trailers")
        return trailer
