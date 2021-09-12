import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class EvolvedFightsSpider(BaseSceneScraper):
    name = 'EvolvedFights'
    network = 'Evolved Fights'

    start_urls = [
        'https://www.evolvedfights.com',
        'https://www.evolvedfightslez.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[@class="updatesBlock"]//span[@class="latest_update_description"]/text()',
        'performers': '//div[@class="updatesBlock"]//span[@class="tour_update_models"]//a/text()',
        'date': '//div[@class="updatesBlock"]//span[@class="update_date"]/text()',
        'image': '//div[@class="updatesBlock"]//span[@class="model_update_thumb"]/img/@src',
        'tags': '//div[@class="updatesBlock"]//span[@class="tour_update_tags"]/a/text()',
        'external_id': 'updates\\/(.*)\\.html',
        'trailer': '//div[@class="updatesBlock"]//div[@class="model_update_block_image"]/a/@onclick',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                if "trailers" in trailer:
                    if "evolvedfightslez" in response.url:
                        trailer = "https://www.evolvedfightslez.com" + \
                            re.search('\\(\'(.*)\'\\)', trailer).group(1)
                    else:
                        trailer = "https://www.evolvedfights.com" + \
                            re.search('\\(\'(.*)\'\\)', trailer).group(1)
                    return trailer
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_site(self, response):
        if "evolvedfightslez" in response.url:
            return "Evolved Fights Lesbian Edition"
        return "Evolved Fights"
