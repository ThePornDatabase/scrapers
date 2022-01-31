import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteModelMediaUSSpider(BaseSceneScraper):
    name = 'ModelMediaUS'
    network = 'Model Media'
    parent = 'Model Media'
    site = 'Model Media US'

    start_urls = [
        'https://www.modelmediaus.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//h3//following-sibling::p/text()',
        'date': '//td[contains(text(), "Released")]/following-sibling::td/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '',
        'performers': '//td[contains(text(), "Cast")]/following-sibling::td/a/text()',
        'tags': '//td[contains(text(), "Tags")]/following-sibling::td/a/text()',
        'external_id': r'.*/(.*?)$',
        'trailer': '',
        'pagination': '/videos?sort=published_at&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "video-preview-media")]/a')
        for scene in scenes:
            image = scene.xpath('./div/img/@src')
            if image:
                image = self.format_link(response, image.get())
            else:
                image = ''
            trailer = scene.xpath('.//video/@data-src')
            if trailer:
                trailer = self.format_link(response, trailer.get())
            else:
                trailer = ''
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image, 'trailer': trailer})
