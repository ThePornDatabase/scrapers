import re
import scrapy
import string
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePornBCNSpider(BaseSceneScraper):
    name = 'PornBCN'
    site = 'PornBCN'
    parent = 'PornBCN'
    network = 'PornBCN'

    start_urls = [
        'https://pornbcn.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "namensmovil")]/div[1]/text()',
        'description': '//h2[contains(text(), "nfo")]/following-sibling::div[1]/p/text()',
        'date': '//img[@alt="fecha video"]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//a[contains(@href, "webp")]/@href',
        'performers': '//span[@class="namepornstarvi"]/span/a/text()',
        'tags': '//meta[@property="article:tag"]/@content',
        'duration': '//img[@alt="tiempo video"]/following-sibling::text()',
        'trailer': '//a[contains(@href, "mp4")]/@href',
        'external_id': r'.*/(.*?)/',
        'pagination': '/en/video/?sf_paged=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoinfo"]/div[1]//a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        performers = self.get_performers(response)
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            tag = tag.lower()
            if re.sub(r'[^a-z]', '', tag):
                tag = GoogleTranslator(source='es', target='en').translate(tag.lower())
            tag = string.capwords(tag)
            if tag not in performers:
                tags2.append(tag)
        return tags2

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            return ""
        return image
