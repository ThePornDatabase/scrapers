import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class FemdomEmpireSpider(BaseSceneScraper):
    name = 'FemdomEmpire'
    network = 'Femdom Empire'

    start_urls = [
        'https://femdomempire.com',
        'http://feminized.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]//h3/text()',
        'description': '//div[contains(@class, "videoDetails")]//p/text()',
        'performers': '//div[contains(@class, "featuring") and contains(., "Featuring")]//following-sibling::li/a/text()',
        'date': '//div[contains(@class, "videoInfo")]//following-sibling::p[contains(., "Date")]/text()',
        'image': '//a[@class="fake_trailer"]//img/@src0_1x',
        'tags': '//div[contains(@class, "featuring") and contains(., "Tags")]//following-sibling::li/a/text()',
        'external_id': '\/trailers\/(.*).html',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/',
    }

    def get_scenes(self, response):
        scenes = self.process_xpath(response, '//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
