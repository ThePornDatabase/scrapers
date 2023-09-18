import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteLexxxiLuxeSpider(BaseSceneScraper):
    name = 'LexxxiLuxe'
    network = 'Lexxxi Luxe'
    parent = 'Lexxxi Luxe'
    site = 'Lexxxi Luxe'

    start_urls = [
        'https://www.lexxxiluxe.com',
    ]

    selector_map = {
        'title': '//h1/span/text()',
        'description': '//div[@class="movie-desc"]/text()',
        'date': '//div[@class="movie-date"]/text()',
        'image': '//script[contains(text(), "videoplayer")]/text()',
        're_image': r'image.*?[\'\"](.*?)[\'\"]',
        'performers': '',
        'tags': '//div[@class="movie-tags"]/div/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'/LEX/(.*?)/',
        'pagination': '/t1/show.php?a=644_%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="itemm"]/a/@href').getall()
        for scene in scenes:
            link = "https://www.lexxxiluxe.com/t1/" + scene
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Lexxxi Luxe']

    def get_title(self, response):
        title = super().get_title(response)
        title = title.strip("\"")
        title = string.capwords(title)
        return title

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace("luxe.com/", "luxe.com/t1/")
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        trailer = trailer.replace("luxe.com/", "luxe.com/t1/")
        return trailer
