import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteExcogigirlsSpider(BaseSceneScraper):
    name = 'Excogigirls'
    network = 'Excogigirls'
    parent = 'Excogigirls'
    site = 'Excogigirls'

    start_urls = [
        'https://excogigirls.com',
    ]

    selector_map = {
        'title': '//section[@id="scene-info"]//h1/text()',
        'description': '//section[@id="scene-info"]//p[@class="description"]//text()',
        'date': '//i[@class="fa fa-calendar"]/following-sibling::text()[contains(., ",")]',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-thumb"]//img/@src0_1x',
        'performers': '//section[@id="model bio"]//h2[@class="model-name"]/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'duration': '//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            meta['trailer'] = self.format_link(response, scene.xpath('./video/source/@src').get())
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "1st" not in tag.lower():
                tags2.append(tag)
        return tags2
