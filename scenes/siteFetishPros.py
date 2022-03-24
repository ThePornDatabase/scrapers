import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFetishProsSpider(BaseSceneScraper):
    name = 'FetishPros'
    network = 'Fetish Pros'
    parent = 'Fetish Pros'
    site = 'Fetish Pros'

    start_urls = [
        'https://www.fetishpros.com',
    ]

    selector_map = {
        'title': '//div[@class="updatesBlock"]/h2/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/updates/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace(".com/content/", ".com/updates/content/")
        return image
