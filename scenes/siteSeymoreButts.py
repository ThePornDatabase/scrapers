import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSeymoreButtsSpider(BaseSceneScraper):
    name = 'SeymoreButts'
    network = 'Seymore Butts'
    parent = 'Seymore Butts'
    site = 'Seymore Butts'

    start_urls = [
        'http://seymorebutts.com',
    ]

    selector_map = {
        'title': '//div[@class="row"]/h1/text()',
        'description': '//h2[contains(text(), "Description")]/following-sibling::p[1]/text()',
        'image': '//div[@id="video_preview"]//a/following-sibling::img/@src',
        'performers': '//h2[contains(text(), "Description")]/following-sibling::p[contains(text(), "Pornstars:")]/a/text()',
        'tags': '//h2[contains(text(), "Description")]/following-sibling::p[contains(text(), "Tags:")]/a/text()',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/videos/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article')
        for scene in scenes:
            scenedate = scene.xpath('.//h3/following-sibling::p/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = scenedate.strip()
                meta['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        if "Unknown" in performers:
            performers.remove("Unknown")
        return performers
