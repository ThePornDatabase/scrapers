import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePrincessReneSpider(BaseSceneScraper):
    name = 'PrincessRene'
    network = 'Princess Rene'
    parent = 'Princess Rene'
    site = 'Princess Rene'

    start_urls = [
        'https://worshiprene.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="description"]//text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'.*datePublished.*?(\d{4}-\d{2}-\d{2}).*',
        'image': '//meta[@property="og:image"]/@content',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/videos/page/%s/?s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="duration"]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get().strip())

            tags = scene.xpath('.//div[@class="terms"]/a/text()')
            if tags:
                meta['tags'] = list(map(lambda x: x.strip().title(), tags.getall()))

            scene = scene.xpath('./div[1]/a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Princess Rene']
