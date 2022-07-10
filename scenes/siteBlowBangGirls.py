import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlowBangGirlsSpider(BaseSceneScraper):
    name = 'BlowBangGirls'
    network = 'Blow Bang Girls'
    parent = 'Blow Bang Girls'
    site = 'Blow Bang Girls'

    start_urls = [
        'https://www.blowbanggirls.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/p//text()',
        'date': '//span[contains(text(), "Added:")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*?\.jpg)',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[contains(text(), "Tags:")]/following-sibling::li/a[contains(@href, "categories")]/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=\"(.*?\.mp4)',
        'external_id': r'.*/(.*?)\.html',
        'pagination': '/v3/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or ".jpg" not in image:
            image = response.xpath('//div[@class="player-thumb"]//img[contains(@class, "update_thumb")]/@src0_2x')
            if image:
                return self.format_link(response, image.get())
        return image
