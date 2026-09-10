import re
import unidecode
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkHiginioDomingoSpider(BaseSceneScraper):
    name = 'HiginioDomingo'
    parent = 'Higinio Domingo'
    network = 'Higinio Domingo'

    start_urls = [
        'https://charmmodels.net',
        'https://domingoview.com',
        'https://letstryhard.com',
        'https://test-shoots.com',
    ]

    # The Elevated X tour is gone (its /categories/movies_N_d.html now answers 410).
    # The sites run their own theme: /updates/ lists div.update-card entries, each
    # carrying the title, model and release date, and the scene page keeps only the
    # h1, og:image and og:description.
    selector_map = {
        'title': '//h1//text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'/updates/(.+?)\.html',
        'pagination': '/updates/page_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "update-card")]'):
            scene = card.xpath('.//a[contains(@class, "update-title")]/@href').get() or card.xpath('./a/@href').get()
            if not scene or not re.search(self.get_selector_map('external_id'), scene):
                continue
            meta = dict(response.meta)

            title = card.xpath('.//a[contains(@class, "update-title")]/text()').get()
            if title and title.strip():
                meta['title'] = self.cleanup_title(title)

            # the scene page carries no date at all; the card is the only source
            scenedate = card.xpath('.//span[contains(@class, "update-date")]/text()').get()
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    meta['date'] = scenedate.group(1)

            performers = [x.strip() for x in card.xpath('.//a[contains(@class, "update-model")]/text()').getall() if x and x.strip()]
            if performers:
                meta['performers'] = performers

            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = unidecode.unidecode(html.unescape(duration.lower().replace("&nbsp;", " ").replace("\xa0", " ")))
            duration = re.sub(r'[^a-z0-9]+', '', duration)
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
