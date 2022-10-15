import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'dreamtranny': "Dream Tranny",
        'jeffsmodels': "Jeffs Models",
    }
    return match.get(argument, argument)

class Spider(BaseSceneScraper):
    name = 'OxygenEnterprises'
    network = 'Oxygen Enterprises'

    start_urls = [
        'https://dreamtranny.com',
        'https://jeffsmodels.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@class="updateDescription"]/p/text()',
        'date': '//span[@class="updateDate"]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[contains(@class,"exclusive_update")]/a/img/@src',
        'performers': '//div[@class="updateModels"]/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/tour/?step=2&cat=latest&page_num=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoThumb"]/a/@href').getall()
        for scene in scenes:
            if "?nats" in scene:
                scene = re.search(r'(.*)\?nats', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        if "dreamtranny" in response.url:
            return ['Trans']

        if "jeffsmodels" in response.url:
            return ['BBW']


    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))
