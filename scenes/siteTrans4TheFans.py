import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTrans4TheFansSpider(BaseSceneScraper):
    name = 'Trans4TheFans'
    site = 'Trans4TheFans'
    parent = 'Trans4TheFans'
    network = 'Trans4TheFans'

    start_urls = [
        'https://trans4thefans.com'
    ]

    selector_map = {
        'title': '//div[@class="breadcrumb"]//span/text()',
        'description': '//h4[contains(text(), "About")]/following-sibling::p/text()',
        'image': '//div[@class="vid-play"]/video/@poster',
        'performers': '//div[@class="pscat"]/a[contains(@href, "pornstars")]/text()',
        'tags': '//div[@class="pscat"]/span/a/text()',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/videos/page/%s/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[@class="vid-listing"]/li')
        for scene in scenes:
            scenedate = scene.xpath('./div[@class="date"]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=["%B %d, %Y"]).strftime('%Y-%m-%d')
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
