import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBaitBuddiesSpider(BaseSceneScraper):
    name = 'BaitBuddies'
    network = 'Bait Buddies'
    parent = 'Bait Buddies'
    site = 'Bait Buddies'

    start_urls = [
        'https://www.baitbuddies.com',
    ]

    selector_map = {
        'description': '//div[@class="TabbedPanelsContentWrap"]//text()',
        'image': '//div[@class="main_video"]/a[1]/img/@src',
        'performers': '//div[@class="header_txt"]/strong/following-sibling::a/text()',
        'tags': '//div[@id="tags"]/a/text()',
        'external_id': r'contentId=(.*?)_',
        'pagination': '/?page=preview&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videos-thumb"]')
        for scene in scenes:
                scenedate = scene.xpath('.//strong[contains(text(), "Release")]/following-sibling::text()')
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.get(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
                scene = scene.xpath('./a/@href').get()
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        performers = self.get_performers(response)
        return " and ".join(performers)
