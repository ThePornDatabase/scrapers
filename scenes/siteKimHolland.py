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
        scenes = response.xpath('//div[@class="movie-item"]')
        for scene in scenes:
            link = scene.xpath('./a[1]/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            # A fresh meta per scene: the previous version mutated response.meta,
            # which is one dict shared by every request off this page, so each
            # card overwrote the last card's date and a card without one silently
            # inherited its neighbour's. The same dict is handed to the next-page
            # request, so a page-1 date also leaked onto the whole archive.
            meta = dict(response.meta)
            meta.pop('date', None)

            scenedate = scene.xpath('.//span[@class="movie-item-date"]/text()').get()
            if scenedate:
                # Cards are written either 02-09-2026 (Dutch day-first) or
                # 2026-08-04. The old formats were '%d-%m-%y', which wants a
                # two-digit year, and '%Y-%m-%D', which is not a Python directive
                # at all -- so neither ever matched and dateparser was left to
                # guess, silently swapping day and month whenever both were <= 12
                # (02-09-2026 was submitted as 9 February).
                scenedate = self.parse_date(scenedate.strip(), date_formats=['%d-%m-%Y', '%Y-%m-%d'])
                if scenedate:
                    meta['date'] = scenedate.strftime('%Y-%m-%d')

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.kimholland.nl"
        else:
            page = str(int(page) - 1)
            return self.format_url(base, self.get_selector_map('pagination') % page)
