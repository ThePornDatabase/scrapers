import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMenOfMontrealSpider(BaseSceneScraper):
    name = 'MenOfMontreal'
    network = 'Men Of Montreal'
    parent = 'Men Of Montreal'
    site = 'Men Of Montreal'

    start_urls = [
        # ~ 'https://menofmontreal.com',  Moved to BroNetwork Scraper
    ]

    selector_map = {
        'title': '//div[contains(@class,"gallery_info")]/h1/text()',
        'description': '//p[@class="update_description"]/text()',
        'date': '',
        'image': '//div[@class="fullscreenTour"]/video-js/@poster',
        'performers': '',
        'tags': '',
        'duration': '//span[@class="availdate"]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/videos_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"category_listing_wrapper")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay Porn']
