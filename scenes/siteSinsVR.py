import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSinsVRSpider(BaseSceneScraper):
    name = 'SinsVR'
    network = 'SinsVR'
    parent = 'SinsVR'
    site = 'SinsVR'

    start_urls = [
        'https://xsinsvr.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//li[contains(@class, "desc")]/div/p//text()',
        'date': '//time/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//dl8-video/@poster',
        'performers': '//strong[contains(text(), "Starring")]/following-sibling::span//a/text()',
        'tags': '//div[@class="tags"]//a/text()',
        'trailer': '//dl8-video/source[1]/@src',
        'external_id': r'/video/(.*)',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="tn-video"]/a[contains(@href, "/video/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
