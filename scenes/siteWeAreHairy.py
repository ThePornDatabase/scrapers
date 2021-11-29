import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWeAreHairySpider(BaseSceneScraper):
    name = 'WeAreHairy'
    network = 'We Are Hairy'
    parent = 'We Are Hairy'
    site = 'We Are Hairy'

    start_urls = [
        'https://www.wearehairy.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="desc"]//h3[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '//time/@datetime',
        'date_formats': ['%Y-%m-%d'],
        'image': '//div[@id="video-wrapper"]//video/@poster',
        'performers': '//div[@class="meet"]/div//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="tagline"]//a[contains(@href, "/categories/")]/text()',
        'external_id': r'.*/(.*?)/',
        'trailer': '//div[@id="video-wrapper"]//video/source/@src',
        'pagination': '/categories/Movies/page%s.shtml'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="dvdtitle"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
