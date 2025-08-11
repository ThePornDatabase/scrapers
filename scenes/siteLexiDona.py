import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLexiDonaSpider(BaseSceneScraper):
    name = 'LexiDona'
    network = 'LexiDona'
    parent = 'LexiDona'
    site = 'LexiDona'

    start_urls = [
        'https://www.lexidona.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "picdetailheader")]/span[1]/following-sibling::a[contains(text(), "avorite")]/preceding-sibling::text()',
        'description': '//div[@class="movie-description"]//text()',
        'date': '//div[contains(@class, "picdetailheader") and contains(text(), "Released")]/strong/em/text()',
        'image': '//video/@poster',
        'external_id': r'.*/video-(.*?)/',
        'pagination': '/videos/page-%s/?tag=all&sort=recent',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[contains(@class, "media-list")]/li')
        for scene in scenes:
            keywords = scene.xpath('.//figcaption/following-sibling::em[1]/text()[1]')
            if keywords:
                keywords = keywords.get()
                meta['tags'] = list(map(lambda x: x.strip().title(), keywords.split(",")))

            duration = scene.xpath('.//figcaption/following-sibling::em[1]//text()[contains(., ":")]')
            if duration:
                duration = duration.get()
                meta['duration'] = self.duration_to_seconds(duration.strip())

            scene = scene.xpath('./a[1]/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Lexi Dona']
