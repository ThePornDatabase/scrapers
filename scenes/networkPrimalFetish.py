import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPrimalFetishSpider(BaseSceneScraper):
    name = 'PrimalFetish'
    network = 'Primal Fetish'
    parent = 'Primal Fetish'
    site = 'Primal Fetish'

    start_urls = [
        'https://primalfetishnetwork.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//span[contains(@class, "update_description")]//text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "update_models")]/a/text()',
        'tags': '//span[@class="tour_update_tags"]/a/text()',
        'trailer': '//a[contains(@onclick, ".mp4")]/@onclick',
        're_trailer': r'(/trailer.*\.mp4)',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateThumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        if " - Primal Fetish" in title:
            title = re.search(r'(.*) - Primal Fetish', title).group(1)
        return title

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "primal" not in tag.lower() and tag.strip()[0] != "." and tag.strip()[:-1] != ".":
                tags2.append(string.capwords(tag.strip()))
        return tags2
