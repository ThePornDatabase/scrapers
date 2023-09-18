import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHimerosTVSpider(BaseSceneScraper):
    name = 'HimerosTV'
    network = 'HimerosTV'
    parent = 'HimerosTV'
    site = 'HimerosTV'

    start_urls = [
        'https://himeros.tv',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="update-info-block"]/p/text()',
        'date': '//div[contains(@class,"update-info-row")]/strong[contains(text(), "Added")]/following-sibling::text()[1]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=[\'\"](.*?)[\'\"]',
        'performers': '//div[contains(@class,"featured-models")]//div[contains(@class, "item-footer")]//a/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//div[contains(@class,"update-info-row")]/strong[contains(text(), "Runtime")]/following-sibling::text()[1]',
        're_duration': r'(\d{1,2}:\d{1,2}:?\d{1,2}?)',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=[\'\"](.*?)[\'\"]',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        for tag in tags:
            if "himeros" in tag.lower():
                tags.remove(tag)
        return tags
