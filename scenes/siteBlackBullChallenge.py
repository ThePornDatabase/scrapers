import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackBullChallengeSpider(BaseSceneScraper):
    name = 'BlackBullChallenge'
    network = 'Black Bull Challenge'
    parent = 'Black Bull Challenge'
    site = 'Black Bull Challenge'

    start_urls = [
        'https://www.blackbullchallenge.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'date': '',
        'image': '//script[contains(text(), "/trailers/")]/text()',
        'image_blob': True,
        're_image': r'src0_3x=\"(http.*?)\".*',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[contains(text(), "Tags:")]/following-sibling::li/a/text()',
        'external_id': r'trailers/(.*).html',
        'trailer': '//script[contains(text(), "/trailers/")]/text()',
        're_trailer': r'video src=\"(.*?\.mp4).*',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if 'Interracial' not in tags:
            tags.append('Interracial')
        return tags

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath('//div[@class="player-window-play"]/following-sibling::img/@src0_3x')
            if image:
                image = self.format_link(response, image.get())
        return image
