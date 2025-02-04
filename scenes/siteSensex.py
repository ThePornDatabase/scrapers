import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSensexSpider(BaseSceneScraper):
    name = 'Sensex'
    network = 'Sensex'
    parent = 'Sensex'
    site = 'Sensex'

    start_urls = [
        'https://www.sensex.com',
    ]

    selector_map = {
        'title': '//section[@id="top-videos"]/div[1]//p[contains(@class, "h3")]/text()',
        'description': '//section[@id="top-videos"]/div[1]/p/text()',
        'date': '',
        'image': '//section[@id="top-videos"]/div[1]/div[1]/div/video/@poster|//section[@id="top-videos"]/div[1]/a//img[contains(@class, "cover")]/@src',
        'performers': '//b[contains(text(), "Featuring")]/following-sibling::text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos/d/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="video-link-overlay"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//b[contains(text(), "Featuring")]/following-sibling::text()')
        if performers:
            performers = performers.get()
            if "&" in performers:
                performers = performers.split("&")
            else:
                performers = [performers]
            performers = list(map(lambda x: string.capwords(x.strip()), performers))
            return performers
        return []
