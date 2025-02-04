import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBoysHalfwayHouseSpider(BaseSceneScraper):
    name = 'BoysHalfwayHouse'
    site = 'BoysHalfwayHouse'
    parent = 'BoysHalfwayHouse'
    network = 'BoysHalfwayHouse'

    start_urls = [
        'https://www.boyshalfwayhouse.com'
    ]

    selector_map = {
        'title': '//div[@class="p-5"]/h2[contains(@class, "blckTitle")]/text()',
        'description': '//div[@class="p-5"]/p/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h5/following-sibling::div/span[contains(@class, "perfImage")]/a/text()',
        'tags': '//h5[contains(text(), "Categories")]/a/text()',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(\d+)-',
        'pagination': '/scenes?sort=published-newer&page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="wrapperSceneTitle"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//h5/i[contains(@class, "clock")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^0-9min]+', '', duration.lower())
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
