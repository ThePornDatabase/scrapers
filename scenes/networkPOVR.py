import dateparser
import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class networkPOVRSpider(BaseSceneScraper):
    name = 'POVR'
    network = 'POVR'
    parent = 'POVR'

    start_urls = [
        'https://povr.com'
    ]

    selector_map = {
        'title': '//h1[@class="player__title"]/text()',
        'description': '//p[contains(@class,"description")]/text()',
        'performers': '//a[contains(@class,"actor")]/text()',
        'date': '//div[@class="player__meta"]/div[3]/span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//a[contains(@class,"tag")]/text()',
        'site': '//a[contains(@class,"source")]/text()',
        'external_id': '.+\/(.*)$',
        'trailer': '',
        'pagination': '/?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="teaser-video"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = self.process_xpath(response, self.get_selector_map('site')).get()
        if site:
            return site  
        return tldextract.extract(response.url).domain
