import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSmokingHawtSpider(BaseSceneScraper):
    name = 'SmokingHawt'
    network = 'Hentaied'
    parent = 'SmokingHawt'
    site = 'SmokingHawt'

    start_urls = [
        'https://smokinghawt.com',
    ]

    cookies = {"name": "age_gate", "value": "18"}

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@id="fullstory"]/p/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//div[contains(@class,"duration")]/img/following-sibling::text()',
        'performers': '//div[@class="taglist"]/a[@rel="tag"]/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'director': '//div[contains(@class,"director")]/span/a/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '//video/source/@src',
        'pagination': '/all-videos/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "SmokingHawt"

    def get_parent(self, response):
        return "SmokingHawt"
