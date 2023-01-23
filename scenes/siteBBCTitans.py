import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBBCTitansSpider(BaseSceneScraper):
    name = 'BBCTitans'
    site = 'BBCTitans'
    parent = 'BBCTitans'
    network = 'BBCTitans'

    start_urls = [
        'https://bbctitans.com/',
    ]

    selector_map = {
        'title': '//div[@class="vid-box"]/h1/text()',
        'description': '//div[@class="vid-box"]/p/text()',
        'date': '',
        'duration': '',
        'image': '//div[@class="vid-play"]/video/@poster',
        'performers': '//div[@class="pscat" and contains(text(), "Pornstars")]/a/text()',
        'tags': '//span[@itemprop="keywords"]/a/text()',
        'external_id': r'\.com/(.*?)/',
        'trailer': '',
        'pagination': '/videos/page/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[@class="vid-listing"]/li')
        for scene in scenes:
            scenedate = scene.xpath('./div[@class="date"]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%B %d, %Y']).isoformat()
            trailer = scene.xpath('.//video/source/@src')
            if trailer:
                meta['trailer'] = self.format_link(response, trailer.get())
            scene = self.format_link(response, scene.xpath('./a/@href').get())
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
