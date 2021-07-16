import dateparser
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
        'title': '//h1/text()',
        'description': '//div[@class="about-video"]/p/text()',
        'performers': '//div[contains(@class,"justify-between")]//div[contains(@class,"models-links")]/a/text()',
        'date': '//meta[@property="og:video:release_date"]/@content',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '',
        'external_id': '.*\/(.*)$',
        'trailer': '',
        'pagination': '/videos/recent?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="models-video"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
