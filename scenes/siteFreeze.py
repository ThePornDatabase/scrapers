import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFreezeSpider(BaseSceneScraper):
    name = 'Freeze'
    network = 'Freeze'
    parent = 'Freeze'
    site = 'Freeze'

    start_urls = [
        'https://freeze.xxx',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@id="fullstory"]/p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//div[contains(@class,"duration")]/img/following-sibling::text()',
        'performers': '//div[contains(@class,"tagsmodels")]/div[contains(@class, "taglist")]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'director': '//div[contains(@class,"director")]/span/a/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '//video/@src',
        'pagination': '/all-videos/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Freeze"

    def get_parent(self, response):
        return "Freeze"
