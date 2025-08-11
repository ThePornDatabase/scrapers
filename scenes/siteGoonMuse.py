import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGoonMuseSpider(BaseSceneScraper):
    name = 'GoonMuse'
    site = 'GoonMuse'
    parent = 'GoonMuse'
    network = 'GoonMuse'

    start_urls = [
        'https://www.goonmuse.com',
    ]

    cookies = [{"name": "warn", "value": "true"}]

    selector_map = {
        'title': '//h4/text()',
        'description': '//div[contains(@class,"vidImgContent")]/p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"latestUpdateBinfo gallery_info")]/p[@class="link_light"]/a/text()',
        'tags': '//div[@class="blogTags"]/ul/li/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoPic"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        sceneid = sceneid.lower().replace("_vids", "")
        return sceneid
