import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHardwerkSpider(BaseSceneScraper):
    name = 'Hardwerk'
    network = 'Hardwerk'
    parent = 'Hardwerk'
    site = 'Hardwerk'

    selector_map = {
        'title': '//div[contains(@class,"video-card-header")]//h2[contains(@class, "video-header")]/text()',
        'description': '//div[contains(@class,"video-card-header")]//p[contains(@class, "video-text")]/text()',
        'image': '//div[contains(@class, "container")]//a[@class="d-block"]/img[@class="img-fluid"]/@src',
        'performers': '//div[contains(@class,"video-card-header")]//h5[contains(text(), "Performers")]/following-sibling::h5/text()',
        'tags': '//div[contains(@class,"video-card-header")]//h5[contains(text(), "Categories")]/following-sibling::h5/text()',
        'trailer': '//video[@id="thisPlayer"]/source/@src',
        'external_id': r'(\d+)\.htm',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        url = 'https://www.hardwerk.com/most-recent/'
        yield scrapy.Request(url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "text-center")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performerlist = response.xpath(self.get_selector_map('performers'))
        if performerlist:
            performerlist = performerlist.get()
            performers = []
            if "," in performerlist:
                performers = performerlist.split(",")
            else:
                performers = [performerlist]
            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []

    def get_tags(self, response):
        taglist = response.xpath(self.get_selector_map('tags'))
        if taglist:
            taglist = taglist.get()
            tags = []
            if "," in taglist:
                tags = taglist.split(",")
            else:
                tags = [taglist]
            return list(map(lambda x: string.capwords(x.strip()), tags))
        return []
