import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAVIdolzSpider(BaseSceneScraper):
    name = 'AVIdolz'
    network = 'AVIdolz'
    parent = 'AVIdolz'
    site = 'AVIdolz'

    start_urls = [
        # ~ 'https://avidolz.com', # Moved into AVRevenue scraper
    ]

    selector_map = {
        'title': '//h1[@itemprop="name"]/text()',
        'description': '//div[@itemprop="description"]//text()',
        'date': '//h1[@itemprop="name"]/../../../../meta[@itemprop="datePublished"]/@content',
        'image': '//h1[@itemprop="name"]/../../../../meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//p/strong[contains(text(), "JAV Model")]/following-sibling::span//text()',
        'tags': '//p/strong[contains(text(), "Categories")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/japan-porn/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[contains(@class, "pure")]/div/div//div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Asian" not in tags:
            tags.append("Asian")
        return tags
