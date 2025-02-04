import re
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLasVegasAmateursSpider(BaseSceneScraper):
    name = 'LasVegasAmateurs'
    site = 'Las Vegas Amateurs'
    parent = 'Las Vegas Amateurs'
    network = 'Exposed Whores Media'

    start_urls = [
        'https://lasvegasamateurs.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]//text()',
        'date': '//span[@class="availdate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//comment()[contains(., "First Thumb Spot")]/following-sibling::a[1]/img/@src0_4x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '//div[@class="update_counts_preview_table"]/text()[contains(., "min")]',
        'trailer': '//div[@class="update_image"]/a[contains(@onclick, ".mp4")][1]/@onclick',
        're_trailer': r'tload.*?(/.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/updates_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/div[1]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()[contains(., "min")]')
        if duration:
            duration = duration.get()
            duration =  re.sub('[^a-z0-9]', '', duration.lower())

            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace(".com/content", ".com/tour/content")
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        trailer = trailer.replace(".com/content", ".com/tour/content")
        return trailer

    def get_id(self, response):
        image = self.get_image(response)
        sceneid = re.search(r'.*/(.*?)/', image).group(1)
        return sceneid.lower()
