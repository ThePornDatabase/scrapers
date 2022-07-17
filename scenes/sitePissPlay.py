import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePissPlaySpider(BaseSceneScraper):
    name = 'PissPlay'
    network = 'Piss Play'
    parent = 'Piss Play'
    site = 'Piss Play'

    start_urls = [
        'https://pissplay.com',
    ]

    selector_map = {
        'title': '//h1[@id="video_title"]/text()',
        'description': '//div[@id="video_description"]/p/text()',
        'date': '//div[@class="video_date"]/text()',
        'date_formats': ['%d %b %Y'],
        'image': '//div[@id="video_player"]/iframe/@src|//div[@id="video_player"]/img/@src',
        'performers': '',
        'tags': '//div[@id="video_tags"]/a/text()',
        'trailer': '',
        'external_id': r'/videos/(.*)',
        'pagination': '/videos/page/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class, "video_thumb")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = self.get_element(response, 'image', 're_image')
            if isinstance(image, list):
                image = image[0]
            link = self.format_link(response, image).replace(' ', '%20')
            if "poster=" in link:
                link = self.format_link(response, re.search(r'poster=(.*\.jpe?g)', link).group(1))
            return link
        return ''
