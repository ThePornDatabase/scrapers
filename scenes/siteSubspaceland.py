import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSubspacelandSpider(BaseSceneScraper):
    name = 'Subspaceland'
    network = 'Subspaceland'

    start_urls = [
        'https://www.subspaceland.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//p[@class="date"]/text()',
        're_date': r'(\d{2} \w{3} \d{4})',
        'date_formats': ['%d %b %Y'],
        'image': '//div[@class="setEntertaiment"]/a/img/@src',
        'performers': '//h2/a[contains(@href,"/model/")]/text()',
        'tags': '//div[@id="tagsInColums"]/ul/li/a/text()',
        'external_id': r'video\/(.*)',
        'trailer': '',
        'pagination': '/movies/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="MovieAsItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        externid = super().get_id(response)
        externid = externid.replace("/", "")
        return externid

    def get_description(self, response):
        return ''

    def get_site(self, response):
        return "Subspaceland"

    def get_parent(self, response):
        return "Subspaceland"
