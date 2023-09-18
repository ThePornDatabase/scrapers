import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSicFlicsSpider(BaseSceneScraper):
    name = 'SicFlics'
    network = 'Sic Flics'
    parent = 'Sic Flics'
    site = 'Sic Flics'

    start_urls = [
        'https://m.sicflics.com',
    ]

    selector_map = {
        'title': '//h1[@class="single-title"]/text()',
        'description': '//div[@class="moviedesc"]/text()',
        'date': '//strong[contains(text(), "Uploaded")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-block"]//img/@src',
        'external_id': r'/c/(\d+)/',
        'pagination': '/cinema/12-chronological-order/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        taglist = response.xpath('//li[contains(text(), "Popular Tags")]/following-sibling::li/div/a/text()')
        if taglist:
            tags = []
            taglist = taglist.getall()
            scenetags = response.xpath('//strong[contains(text(), "Related Tags")]/following-sibling::a/text()')
            if scenetags:
                scenetags = scenetags.getall()
                for scenetag in scenetags:
                    if "#" in scenetag:
                        scenetag = scenetag.replace('#', '').lower()
                    if scenetag in taglist:
                        tags.append(string.capwords(scenetag))
                return tags
        return []

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("‘", "'").replace("’", "'")
        return description
