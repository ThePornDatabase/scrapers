# Can't access more than initial index page
import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAmelieLouSpider(BaseSceneScraper):
    name = 'AmelieLou'
    network = 'Superbe Models'
    parent = 'Amelie Lou'
    site = 'Amelie Lou'

    start_urls = [
        'https://www.amelielou.com/films/',
    ]

    def start_requests(self):
        url = 'https://www.amelielou.com/films/'
        yield scrapy.Request(url, callback=self.get_scenes, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"description-video")]/p/text()',
        'date': '//span[contains(text(), "Release date")]/following-sibling::em/text()',
        'image': '//script[contains(text(), "preview_url")]/text()',
        're_image': r'.*preview_url:.*?(http.*?\.jpg).*',
        'performers': '',
        'tags': '//span[@class="title-tag-video"]/following-sibling::a/text()',
        'external_id': r'films/(\d+)/',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href, "/films/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        return ['Amelie Lou']

    def get_tags(self, response):
        tags = super().get_tags(response)
        if tags:
            tags = list(map(lambda x: x.replace(",", ""), tags))
        return tags
