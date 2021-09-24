import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTouchMyWifeSpider(BaseSceneScraper):
    name = 'TouchMyWife'
    network = 'Touch My Wife'

    start_urls = [
        'https://www.touchmywife.com',
    ]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//div[@class="synopsis"]//text()',
        'date': '//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"video-performer-container")]/div/a/span/span/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': r'(\d{4,7})/',
        'trailer': '',
        'pagination': '/watch-newest-clips-and-scenes.html?page=%s&view=grid'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="grid-item"]/div[@class="grid-item"]')
        for scene in scenes:
            trailer = scene.xpath('.//source/@src')
            if trailer:
                trailer = trailer.get()
            else:
                trailer = False
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'trailer': trailer})

    def get_site(self, response):
        return "Touch My Wife"

    def get_parent(self, response):
        return "Touch My Wife"
