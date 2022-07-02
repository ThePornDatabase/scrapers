import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWankitnowVRSpider(BaseSceneScraper):
    name = 'Wankitnowvr'
    network = 'Wankitnowvr'
    parent = 'Wankitnowvr'
    site = 'Wankitnowvr'

    start_urls = [
        'https://wankitnowvr.com',
    ]

    selector_map = {
        'title': '//div[@class="col"]/h2/text()',
        'description': '//div[@class="col"]/h2/following-sibling::p//text()',
        'date': '//div[@class="col"]/p[1]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//deo-video/@cover-image',
        're_image': r'(.*\.jpg)',
        'performers': '//div[@class="col"]/p[1]//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="col"]/p[1]//a[contains(@href, "/videos/")]/text()',
        'trailer': '//deo-video/source[1]/@src',
        'external_id': r'.*/(\d+)',
        'pagination': '/videos?order=&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "card")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = list(map(lambda x: string.capwords(x.lower().replace("(toys)", "").replace("(action)", "").replace("(outfit)", "").replace("(body)", "").replace("(", "").replace(")", "").replace("nationality", "").replace("location", "")).strip(), tags))
        taglist = []
        for tag in tags:
            if not "quality" in tag.lower() and " age" not in tag.lower():
                taglist.append(tag)
        return taglist

    def get_date(self, response):
        if 'date' in self.get_selector_map():
            scenedate = response.xpath(self.get_selector_map('date'))
            if scenedate:
                scenedate = scenedate.getall()
                scenedate = " ".join(scenedate)
                scenedate = re.search(self.get_selector_map('re_date'), scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    date_formats = self.get_selector_map('date_formats') if 'date_formats' in self.get_selector_map() else None
                    return self.parse_date(self.cleanup_text(scenedate), date_formats=date_formats).isoformat()
