import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SugarDaddyPornSpider(BaseSceneScraper):
    name = 'SugarDaddyPorn'
    network = 'Sugar Daddy Porn'
    parent = 'Sugar Daddy Porn'

    start_urls = [
        'https://www.sugardaddyporn.com'
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'performers': '//nav[contains(@class,"video__actors")]/a/text()',
        'date': '//meta[@property="og:video:release_date"]/@content',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class,"video__tags")]/a/text()',
        'duration': '//span[contains(@class, "duration")]/time/text()',
        'external_id': r'.*/(.*)$',
        'trailer': '',
        'pagination': '/videos/recent/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="image-container"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene.strip()), callback=self.parse_scene)
