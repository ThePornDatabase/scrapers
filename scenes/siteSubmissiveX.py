import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSubmissiveXSpider(BaseSceneScraper):
    name = 'SubmissiveX'
    network = 'Submissive X'
    parent = 'Submissive X'
    site = 'Submissive X'

    start_urls = [
        'https://submissivex.com/',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
