import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSinfulFeetSpider(BaseSceneScraper):
    name = 'SinfulFeet'
    network = 'Sinful Feet'
    parent = 'Sinful Feet'
    site = 'Sinful Feet'

    start_urls = [
        'https://www.sinfulfeet.com',
    ]

    selector_map = {
        'title': '//article[contains(@class, "main-article")]/section[1]//div[contains(@class, "title-block")]/h2[contains(@class, "section-title")]/text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::text()',
        'date': '//strong[contains(text(), "Released")]/following-sibling::text()',
        'image': '//img[contains(@class, "update_thumb")]/@src0_1x',
        'performers': '//div[contains(@class, "models-list-thumbs")]/ul/li/a//span/text()',
        'tags': '//h3[contains(text(), "Tags")]/following-sibling::ul/li/a/text()',
        'duration': '//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "_videothumb_")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            meta['id'] = re.search(r'b(\d+)_', sceneid).group(1)

            scene = scene.xpath('./a/@href').get()

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
