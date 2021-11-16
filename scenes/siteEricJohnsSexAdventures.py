import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEricJohnsSexAdventuresSpider(BaseSceneScraper):
    name = 'EricJohnsSexAdventures'
    network = 'Eric Johns Sex Adventures'
    parent = 'Eric Johns Sex Adventures'
    site = 'Eric Johns Sex Adventures'

    start_urls = [
        'https://ericjohnssexadventures.com',
    ]

    selector_map = {
        'title': '//h2[@class="section-title"]/text()',
        'description': '//h3[contains(text(),"Description:")]/following-sibling::text()',
        'date': '',
        'image': '//img[@class="update_thumb thumbs stdimage"]/@src0_1x',
        'performers': '//li/a/span/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-div"]/h4/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
