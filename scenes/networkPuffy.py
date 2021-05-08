import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PuffySpider(BaseSceneScraper):
    name = 'PuffyNetwork'
    network = "Puffy Network"
    parent = "Puffy Network"

    start_urls = [
        'https://www.puffynetwork.com/',
    ]

    selector_map = {
        'title': "//h2[@class='title']/span/text()",
        'description': "//section[@class='downloads']//div[@class='show_more']/text()",
        'date': "//section[contains(@class, 'downloads2')]/dl[1]/dt[2]/span/text()",
        'image': "//video[1]/@poster",
        'performers': "//section[contains(@class, 'downloads2')]/dl[1]/dd[1]//a/text()",
        'tags': "",
        'external_id': 'videos/(.+)/?$',
        'trailer': '',
        'pagination': '/videos/page-%s/?&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//article[@id='updates-list']//li//a[1]/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
