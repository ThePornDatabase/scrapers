import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


# Non-JSON based spider, scrapes individual pages

class SexLikeRealAltSpider(BaseSceneScraper):
    name = 'SexLikeRealAlt'
    network = 'SexLikeReal'

    start_urls = [
        # ~ 'https://www.sexlikereal.com'
    ]

    selector_map = {
        'title': "//h1/text()",
        'description': "//div[@class='u-mt--three']/div[contains(@class,'u-lw')]/text()",
        'date': "//div[@class='u-mt--three']//div[contains(text(),'Released')]/following-sibling::time/text() | //time/@datetime",
        'performers': "//ul[contains(@class,'scene-models')]/li/a/text()",
        'tags': "//meta[@property='video:tag']/@content",
        'external_id': r'.*-(\d+).*?$',
        'image': '//meta[@property="og:image"]/@content',
        'trailer': '',
        'pagination': '/scenes?type=new&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/div/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[@class="u-block"]/span/a/span/text()').get()
        if site:
            return site.strip()
        return "Sex Like Real"

    def get_parent(self, response):
        parent = response.xpath('//div[@class="u-block"]/span/a/span/text()').get()
        if parent:
            return parent.strip()
        return "Sex Like Real"

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []
