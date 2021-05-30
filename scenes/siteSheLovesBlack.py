import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

class SheLovesBlackSpider(BaseSceneScraper):
    name = 'SheLovesBlack'
    network = 'She Loves Black'

    start_urls = [
        'https://www.shelovesblack.com'
    ]


    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//p[contains(@class, "description")]/text()',
        'performers': '//div[contains(@class, "featured")]/a/text()',
        'date': '//div[contains(@class, "date")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "video-tags")]/a/text()',
        'trailer': '',
        'external_id': 'trailers/(.*)\.html',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"item-video-overlay")]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)