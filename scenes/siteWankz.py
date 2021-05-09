import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class WankzSpider(BaseSceneScraper):
    name = 'Wankz'
    network = "Wankz"

    start_urls = [
        'https://www.wankz.com'
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': "//div[@class='views']/span/text()",
        'image': '//a[@class="noplayer"]/img/@src',
        'performers': '//div[@class="models-wrapper actors"]/a/span/text()',
        'tags': "//a[@class='cat']/text()",
        'external_id': '-(\\d+)$',
        'trailer': '',
        'pagination': '/videos?p=%s#'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[@class='title-wrapper']/a/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        search = re.search('span>Added\\ (.*?)<\\/span', response.text)
        scenedate = dateparser.parse(search.group(1)).isoformat()
        return scenedate

    def get_site(self, response):
        site = response.xpath(
            '//div[@class="inner"]/div/p/a[@class="sitelogom"]/img/@alt').get().strip()
        return site
