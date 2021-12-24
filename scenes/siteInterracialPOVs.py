# This site is no longer updated, and has been combined with HussiePass
# going forward.  Only writing scraper to pull existing old scenes

import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteInterracialPOVsSpider(BaseSceneScraper):
    name = 'InterracialPOVs'
    network = 'Interracial POVs'
    parent = 'Interracial POVs'
    site = 'Interracial POVs'

    start_urls = [
        'https://www.interracialpovs.com',
    ]

    selector_map = {
        'title': '//div[@class="videoDetails clear"]/h3/text()',
        'description': '//div[@class="videoDetails clear"]/p/text()',
        'date': '//span[contains(text(), "Date")]/following-sibling::text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//div[@class="featuring clear"]/ul/li/a[contains(@href, "categories")]/text()',
        'external_id': r'trailers/(.*).html',
        'trailer': '',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "4K" in tags:
            tags.remove("4K")
        if "4k" in tags:
            tags.remove("4k")
        if "Pov/Selfshot" in tags:
            tags.remove("Pov/Selfshot")
            tags.append("POV")
        return tags
