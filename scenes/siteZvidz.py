import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteZvidzSpider(BaseSceneScraper):
    name = 'Zvidz'
    network = 'Zvidz'
    parent = 'Zvidz'
    site = 'Zvidz'

    start_urls = [
        'https://www.zvidz.com',
    ]

    selector_map = {
        'title': '//div[@id="meta-data"]/h1/text()',
        'description': '//div[@id="player-join-footer"]/p/a/text()',
        'date': '',
        'image': '//script[contains(text(), "jwplayer")]/text()',
        're_image': r'image:\s+?\"(.*?\.jpg)',
        'performers': '//p[@class="cast-list"]/a/text()',
        'tags': '//p[@class="tags-list"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "jwplayer")]/text()',
        're_trailer': r'file:\s+?\"(.*?\.mp4)',
        'pagination': '/categories/scenes_d.html?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "scene-grid-item")]')
        for scene in scenes:
            meta = {}
            date = scene.xpath('.//strong[contains(text(), "Released")]/following-sibling::text()[1]')
            if date:
                meta['date'] = self.parse_date(date.get()).isoformat()
            else:
                meta['date'] = self.parse_date('today').isoformat()
            meta['id'] = re.search(r'item-(\d+)', scene.xpath('./@id').get()).group(1)
            scene = scene.xpath('./div[@class="scene-grid-image-container"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = super().get_description(response).strip()
        if description:
            description = "From: " + description
        description_paragraph = response.xpath('//p[contains(@class,"description")]/text()')
        if description_paragraph:
            description_paragraph = description_paragraph.get().strip()
            description = description_paragraph + "   (" + description + ")"
        return description
