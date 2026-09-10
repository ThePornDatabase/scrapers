import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSketchySexSpider(BaseSceneScraper):
    name = 'SketchySex'
    network = 'Sketchy Sex'
    parent = 'Sketchy Sex'
    site = 'Sketchy Sex'

    start_urls = [
        'https://www.sketchysex.com',
    ]

    selector_map = {
        'title': '//div[@class="info"]/div[@class="name"]/span/text()',
        'description': '//div[@class="VideoDescription"]/text()',
        'image': '//video/@poster',
        'performers': '//ul[@class="ModelNames"]/li/a/text()',
        'tags': '//div[@class="VideoTagsWrap"]/a/span/text()',
        'external_id': r'id=(\d+)',
        'pagination': '/index.php?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="video-item"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[contains(@class, "video-date")]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get().strip(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            scene = scene.xpath('./div[contains(@class,"video-thumb")]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.extend(['Gay'])
        return tags