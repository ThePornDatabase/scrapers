import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class BabeArchivesWhoresSpider(BaseSceneScraper):
    name = 'BabeArchives'
    network = 'Babe Archives'
    parent = 'Babe Archives'

    start_urls = [
        'https://babearchives.com'
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/h3/text()',  # No description on site, just using title for filler
        'date': '//span[contains(text(),"Added:")]/following-sibling::text()',
        'image': '//div[@class="player-thumb"]/img/@src0_1x',
        'image_blob': True,
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '',
        'external_id': r'\/trailers\/(.+)\.html',
        'trailer': '',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-info"]/h4/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta={'site': 'Babe Archives'})
