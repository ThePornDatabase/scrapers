import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCorbinFisherSpider(BaseSceneScraper):
    name = 'CorbinFisher'
    network = 'Corbin Fisher'
    parent = 'Corbin Fisher'
    site = 'Corbin Fisher'

    start_urls = [
        'https://www.corbinfisher.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"blogSpace")]/h2/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '//span[contains(text(), "Added:")]/following-sibling::text()[1]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-thumb"]/img/@src0_1x',
        'image_blob': True,
        'performers': '//div[contains(@class, "blogSpace")]//div[contains(@class, "modelFeaturing")]//ul/li/a/text()',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-description"]/h4/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
