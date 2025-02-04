import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDrillHimSpider(BaseSceneScraper):
    name = 'DrillHim'
    site = 'DrillHim'
    parent = 'DrillHim'
    network = 'DrillHim'

    start_urls = [
        'https://drillhim.com'
    ]

    selector_map = {
        'title': '//div[@class="episode-title"]//h2/text()',
        'description': '',
        'date': '//div[@class="episode-title"]/span[not(h2)]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//ul[contains(@class,"under-episode-thumbnails")]/li[1]/img/@src',
        're_image': r'\.?(.*)',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'id=(\d+)',
        'pagination': '/tour.php?p=%s',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % str(int(page) - 1))

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="content-wrapper"]')
        for scene in scenes:
            duration = scene.xpath('./p[not(contains(./a/@href, "php"))]/text()')
            if duration:
                duration = duration.get()
                meta['duration'] = self.duration_to_seconds(duration)
            scene = scene.xpath('./p/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
