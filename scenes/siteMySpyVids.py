import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMySpyVids(BaseSceneScraper):
    name = 'MySpyVids'
    site = 'MySpyVids'

    start_urls = [
        'https://www.myspyvids.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/text()',
        'description': '//div[@class="desc"]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="pl_scr"]/img/@src',
        'duration': '//div[@class="runtime"]/text()',
        'tags': '//div[@class="category"]/a/text()',
        'external_id': r'/([^/]+)\.html$',
        'trailer': '',
        'pagination': '/movies/%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="scr_block"]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="runtime"]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d{1,2}:\d{1,2})', duration)
                if duration:
                    duration = duration.group(1)
                    meta['duration'] = self.duration_to_seconds(duration)
            scene = scene.xpath('.//div[@class="watch_link"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = super().get_id(response)
        sceneid = re.sub(r'[^a-z0-9]+', '', sceneid.lower())
        return sceneid
