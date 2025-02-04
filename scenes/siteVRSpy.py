import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRSpySpider(BaseSceneScraper):
    name = 'VRSpy'
    site = 'VRSpy'
    parent = 'VRSpy'
    network = 'VRSpy'

    start_urls = [
        'https://vrspy.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "section-header-container")]/text()',
        'description': '//div[contains(@class,"show-more-text-container")]//text()',
        'date': '//div[contains(text(), "Release date")]/span[1]/text()|//div[contains(text(), "Release date")]/following-sibling::div[1]/text()',
        'date_formats': ['%d %B %Y'],
        'image': '//meta[@property="og:image"]/@content[contains(., "cover")]',
        'performers': '//div[contains(@class,"video-actor-item")]/span/text()',
        'tags': '//div[@class="video-categories"]/a//text()',
        'duration': '//div[contains(text(), "Duration:")]/span[1]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"info--grid")]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//script[contains(@id, "NUXT_DATA")]/text()')
        if image:
            image = image.get()
            image = re.search(r'\"Video\".*?(https.*?cover.jpg)', image)
            if image:
                image = image.group(1)
                if image not in response.url:
                    return image
        return ""
