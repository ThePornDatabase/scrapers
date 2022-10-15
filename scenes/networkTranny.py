import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkTrannySpider(BaseSceneScraper):
    name = 'Tranny'
    network = 'Tranny.Com'
    parent = 'Tranny.Com'

    start_urls = [
        'https://www.tranny.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/h1/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '//span[contains(text(), "Added")]/text()',
        're_date': r'(\d{1,2} \w+ \d{4})',
        'date_formats': ['%d %B %Y'],
        'duration': '//div[@class="title"]/span[contains(@class, "time")]',
        're_duration': r'\((.*?\d{1,2}:\d{2}) ',
        'image': '//a[@class="noplayer"]/img/@src',
        'performers': '//div[@class="information"]//a[@class="model"]//span/text()',
        'tags': '//span[contains(text(), "Categories")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'.*?-(\d+)$',
        'pagination': '/videos?p=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="scene"]/div/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//div[@class="inner"]//p//a[contains(@href, "/sites/")]/text()')
        if site:
            return self.cleanup_title(site.get())
        return "Tranny.Com"

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Trans" not in tags:
            tags.append("Trans")
        return tags
