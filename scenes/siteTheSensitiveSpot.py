import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTheSensitiveSpotSpider(BaseSceneScraper):
    name = 'TheSensitiveSpot'
    network = 'The Sensitive Spot'
    parent = 'The Sensitive Spot'
    site = 'The Sensitive Spot'

    start_urls = [
        'https://thesensitivespot.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//div[@class="contentD"]//i[contains(@class, "calendar")]/following-sibling::text()',
        'date_formats': ['%m %d, %Y'],
        'image': '//meta[@name="twitter:image"]/@content',
        # ~ 'image': '//div[contains(@class, "videoPreview")]//iframe/@src',
        # ~ 're_image': r'poster=(http.*)',
        'performers': '//div[@class="models"]/ul/li/a/text()',
        # ~ 'tags': '//div[@class="tags"]/ul/li/a/text()',
        'duration': '//div[@class="contentD"]//i[contains(@class, "clock")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoPic"]')
        for scene in scenes:
            sceneid = scene.xpath('./a/img/@src').get()
            sceneid = re.search(r'thumbs/(\d+)/', sceneid)
            if sceneid:
                meta['id'] = sceneid.group(1)

            scene = scene.xpath('./a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
