import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteUnlimitedMILFsSpider(BaseSceneScraper):
    name = 'UnlimitedMILFs'
    network = 'New Sensations'
    parent = 'Unlimited MILFs'
    site = 'Unlimited MILFs'

    start_urls = [
        'https://network.newsensations.com',
    ]

    selector_map = {
        'title': '//div[@class="update_title"]/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="cell update_date"]/text()',
        're_date': r'Released: (.*)',
        'date_formats': ['%m/%d/%Y'],
        'image': '//video/@poster|//div[@id="hpromo"]/a/img/@src',
        'performers': '//span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'scenes/(.*).html',
        'trailer': '',
        'pagination': '/tour_um/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
