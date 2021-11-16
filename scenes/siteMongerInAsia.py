import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMongerInAsiaSpider(BaseSceneScraper):
    name = 'MongerInAsia'
    network = 'Monger In Asia'
    parent = 'Monger In Asia'
    site = 'Monger In Asia'

    start_urls = [
        'https://mongerinasia.com',
    ]

    selector_map = {
        'title': '//div[@class="scene-title-wrap"]/h1/text()',
        'description': '//div[contains(@class,"description_content")]/text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '//div[@class="div-model-info-in-desc"]//h2/text()',
        'tags': '',
        'external_id': r'trailers/(.*)',
        'trailer': '//video/source/@src',
        'pagination': '/categories/monger-in-asia_%s_d'
    }

    def get_scenes(self, response):
        meta = {}
        scenes = response.xpath('//div[contains(@class,"videoBlock")]')
        for scene in scenes:
            date = scene.xpath('./div[@class="scene-icons"]//img[contains(@class,"calendar")]/following-sibling::span/text()')
            if date:
                meta['date'] = self.parse_date(date.get()).isoformat()
            tag = scene.xpath('.//a[@class="site_link"]/span/text()')
            if tag:
                meta['tags'] = [tag.get().strip()]

            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
