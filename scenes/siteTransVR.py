import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTransVRSpider(BaseSceneScraper):
    name = 'TransVR'
    site = 'TransVR'
    parent = 'TransVR'
    network = 'Grooby Network'

    start_urls = [
        'https://www.transvr.com'
    ]

    selector_map = {
        'title': '//dl8-video/@title',
        'description': '//div[@class="set_meta"]/following-sibling::p[1]//text()',
        'date': '//div[@class="set_meta"]/b/following-sibling::text()[1]',
        'image': '//dl8-video/@poster',
        'performers': '//div[@class="trailer_toptitle_left"]/a/text()',
        'tags': '//div[@class="set_tags"]/ul/li/a/text()',
        'duration': '//div[@class="set_meta"]/i[contains(@class, "play-circle")]/following-sibling::text()[1]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        're_external_id': r'set-target-(\d+)',
        'pagination': '/tour/categories/movies/%s/latest/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoblock"]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        image = super().get_image(response)
        sceneid = re.search(r'.*/(\d+)', image).group(1)
        return sceneid

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Virtual Reality")
        return tags
