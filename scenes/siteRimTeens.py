import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRimTeensSpider(BaseSceneScraper):
    name = 'RimTeens'
    site = 'RimTeens'
    parent = 'RimTeens'
    network = 'RimTeens'

    start_urls = [
        'https://rimteens.com'
    ]

    selector_map = {
        'title': '//h1[contains(@class, "entry-title")]/text()',
        'description': '//div[contains(@class, "entry-content")]//text()',
        'date': '//h1/following-sibling::p[1]//time[@class="entry-date"]/@datetime',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h2[contains(@class, "author-title")]/a/span/text()',
        'tags': '//div[contains(@class, "after-content")]/p[1]//a/text()',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/',
        'pagination': '/page/%s/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[contains(./span/text(), "LATEST")]/following-sibling::div[1]//article')
        for scene in scenes:
            duration = scene.xpath('.//span[contains(@class, "video-duration")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())
            scenedate = scene.xpath('.//time/@datetime')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)
            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
