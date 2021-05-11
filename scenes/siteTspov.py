import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class TSPOV(BaseSceneScraper):
    name = 'TSPOV'
    network = 'TSPOV'

    start_urls = [
        'https://www.tspov.com/',
    ]

    selector_map = {
        'title': '//div[contains(@class, "titlebox")]//h3/text()',
        'description': '//div[contains(@class, "aboutvideo")]//p/text()',
        'performers': '//ul[contains(@class, "featuredModels")]/li//span/text()',
        'date': '//div[contains(@class, "video_description")]//h4/text()',
        're_date': r'\b(\d{1,4}-\d{1,2}-\d{1,2})\b',
        'image': '//div[contains(@class, "videohere")]//img/@src',
        'tags': '',
        'trailer': '',
        'external_id': '/trailers/(.*).html',
        'pagination': '/tour/updates/page_%s.html',

    }

    def get_scenes(self, response):
        scenes = response.xpath('//body//section[2]//div[@class="empireimg"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
