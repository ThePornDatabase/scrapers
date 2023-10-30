import re
# ~ import string
# ~ from deep_translator import GoogleTranslator
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKimHollandSpider(BaseSceneScraper):
    name = 'KimHolland'
    network = 'Kim Holland'
    parent = 'Kim Holland'
    site = 'Kim Holland'

    start_urls = [
        'https://www.kimholland.nl',
    ]

    cookies = {'khlanguage': 'NL'}

    selector_map = {
        'title': '//h1[contains(@id, "title")]/text()',
        'description': '//div[contains(@class, "player-description")]/text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/archief-%s.html?lang=nl',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta

        scenes = response.xpath('//div[@class="movie-item"]')
        for scene in scenes:
            if int(meta['page']) == 1:
                scenedate = scene.xpath('.//span[@class="movie-item-date"]/text()')
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = self.parse_date(scenedate, date_formats=['%d-%m-%y', '%Y-%m-%D']).strftime('%Y-%m-%d')
                    if scenedate:
                        meta['date'] = scenedate
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.kimholland.nl"
        else:
            page = str(int(page) - 1)
            return self.format_url(base, self.get_selector_map('pagination') % page)
