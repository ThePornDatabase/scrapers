import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTakeVanSpider(BaseSceneScraper):
    name = 'TakeVan'
    network = 'Take Van'
    parent = 'Take Van'
    site = 'Take Van'

    start_urls = [
        'https://takevan.com',
    ]

    selector_map = {
        'title': '//header/h1[contains(@class, "videoTitle")]/text()',
        'description': '//div[@class="videoDescription"]/text()',
        'image': '//div[@class="video"]/div[@class="player"]/img/@src',
        'performers': '//div[@class="videoFeaturedModels"]/text()',
        'tags': '//div[@class="videoTags"]/a/text()',
        'trailer': '',
        'external_id': r'video/(\d+)/',
        'pagination': '/pickups/?p=%s'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="blockItem"]')
        for scene in scenes:
            scenedate = scene.xpath('.//li[@class="detailDate"]/span/text()')
            # parse_date returns a datetime; the pipeline expects a date string
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
            else:
                meta['date'] = self.parse_date('today').strftime('%Y-%m-%d')
            scene = scene.xpath('./article/figure/a/@href').get()
            # Roughly a third of the blockItem divs are MMP Network ad banners with no
            # scene link at all, which made re.search() raise on None.
            if not scene:
                continue
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        if "," in performers:
            performers = performers.split(",")
            performers = list(map(lambda x: self.cleanup_title(x.strip()), performers))
        return performers
