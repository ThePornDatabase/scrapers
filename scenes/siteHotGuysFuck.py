import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class HotGuysFuckSpider(BaseSceneScraper):
    name = 'HotGuysFuck'
    network = "Hot Guys Fuck"
    parent = "Hot Guys Fuck"

    start_urls = [
        'https://www.hotguysfuck.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[@class="descriptionIntro"]/p/text()',
        'date': '//meta[@property="og:video:release_date"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//meta[@property="og:video:actor"]/@content',
        'tags': '//meta[@property="og:video:tag"]/@content',
        'trailer': '',
        'external_id': r'video\/(.*)',
        'pagination': '/videos/recent?page=%s'
    }

    def get_scenes(self, response):

        scenes = response.xpath(
            '//div[@class="thumbWrapper"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Hot Guys Fuck"
