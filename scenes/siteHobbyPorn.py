import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHobbyPornSpider(BaseSceneScraper):
    name = 'HobbyPorn'
    network = 'HobbyPorn'
    parent = 'HobbyPorn'

    start_urls = [
        'https://hobby.porn',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@itemprop="description"]/text()',
        'date': '//strong[contains(text(), "Published")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@itemprop="author"]/a/text()',
        'tags': '//strong[contains(text(), "Categories") or contains(text(), "Tags")]/following-sibling::a/text()',
        'duration': '//strong[contains(text(), "Duration")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-video")]/a[contains(@href, "video")][1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        image = super().get_image(response)
        sceneid = re.search(r'.*/(\d+)/', image).group(1)
        return sceneid

    def get_site(self, response):
        performers = super().get_performers(response)
        return "HobbyPorn: " + performers[0]
