import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAdulttimeLadyGonzoSpider(BaseSceneScraper):
    name = 'LadyGonzo'
    network = 'Gamma Enterprises'
    parent = 'Lady Gonzo'
    site = 'Lady Gonzo'

    start_urls = [
        'https://www.ladygonzo.com',
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text()',
        'description': '//div[contains(@class, "sceneDescText")]//text()',
        'date': '//span[@class="updatedDateSpan"]/following-sibling::text()',
        'date_formats': ['%m-%d-%Y'],
        'image': '//script[contains(text(), "picPreview")]/text()',
        're_image': r'picPreview.*?(http.*?\.jpg)',
        'performers': '//div[@id="slick_sceneInfoActorCarousel"]//span[@class="slide-title"]/text()',
        'tags': '//div[@class="sceneCategories"]/span/text()',
        'trailer': '//script[contains(text(), ".mp4")]/text()',
        're_trailer': r'\"url\":\"(.*?\.mp4)',
        'external_id': r'.*/(\d+)',
        'pagination': '/en/videos?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class, "scene")]/div/a/@href').getall()
        for scene in scenes:
            meta['id'] = re.search(r'.*/(\d+)', scene).group(1)
            meta['url'] = self.format_link(response, scene)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title = title.replace("|", "-")
        return title

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace('\\', '')
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        trailer = trailer.replace('\\', '')
        if "jpg" in trailer:
            trailer = re.search(r'\"src.*?(http.*?\.mp4)', trailer).group(1)
        return trailer
