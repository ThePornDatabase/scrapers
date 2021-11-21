import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePawgedSpider(BaseSceneScraper):
    name = 'PAWGED'
    network = 'PAWGED'
    parent = 'PAWGED'
    site = 'PAWGED'

    start_urls = [
        'https://pawged.com/',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="update_block_info"]/span[@class="tour_update_models"]/a/text()',
        'tags': '//div[@class="update_block_info"]/span[@class="update_tags"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//div[@class="update_image"]/a/@onclick',
        're_trailer': '\'(.*.mp4)\'',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updatesAreaTop"]//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return "https://pawged.com/tour/" + trailer.replace(" ", "%20")

        return ''

    def get_id(self, response):
        return super().get_id(response).lower()
