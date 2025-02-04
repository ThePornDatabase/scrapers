import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePublicHandjobsSpider(BaseSceneScraper):
    name = 'PublicHandjobs'
    site = 'Public Handjobs'
    parent = 'Public Handjobs'
    network = 'Public Handjobs'

    start_urls = [
        'https://publichandjobs.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h4[contains(text(), "Tags")]/following-sibling::p//text()',
        'image': '//video/@poster',
        'performers': '',
        'tags': '//h4[contains(text(), "Tags")]/a/text()',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/page%s/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video-card"]')
        for scene in scenes:
            sceneid = scene.xpath('./div/a/img/@src').get()
            meta['id'] = re.search(r'/(\d+)-', sceneid).group(1)
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//h4[contains(text(), "Model:")]/text()').get()
        performers = re.search(r':(.*)', performers).group(1)
        performers = performers.strip().replace("  ", " ")
        performers = performers.split(" and ")
        return performers
