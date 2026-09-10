import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGuysInSweatpantsSpider(BaseSceneScraper):
    name = 'GuysInSweatpants'
    network = 'Guys In Sweatpants'
    parent = 'Guys In Sweatpants'
    site = 'Guys In Sweatpants'

    cookies = {"pp-accepted": "true"}

    start_urls = [
        'https://guysinsweatpants.com',
    ]

    # The site moved onto a /tour/ build: /scenes is a 404 and li.gallery-item-1 is
    # gone, along with h1.title and the div.meta block every field hung off.  The
    # listing is /tour/categories/movies.html (movies_N.html from page 2), cards are
    # div.item-video, and the scene page keeps its facts in labelled
    # span.update-info-title / span.update-info-value pairs.
    selector_map = {
        'title': '//h3[contains(@class, "highlight")]/text()',
        'description': '//div[contains(@class, "update-info-block") and contains(@class, "text-larger")]//text()',
        'date': '//span[contains(text(), "RELEASE DATE")]/following-sibling::span[1]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '',
        'performers': '//span[contains(text(), "CAST")]/following-sibling::span[1]//a/text()',
        'tags': '',
        'duration': '//span[contains(text(), "SCENE LENGTH")]/following-sibling::span[1]/text()',
        'trailer': '',
        'external_id': r'/trailers/([^/?]+)\.html',
        'pagination': '/tour/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return self.format_url(base, '/tour/categories/movies.html')
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "item-video")]'):
            link = card.xpath('.//div[contains(@class, "item-title")]//a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            # the still is only on the card; the scene page shows the player instead
            image = card.xpath('.//img/@src0_1x').get() or card.xpath('.//img/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)
            preview = card.xpath('.//div[@data-videosrc]/@data-videosrc').get()
            if preview:
                meta['trailer'] = self.format_link(response, preview)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        return response.meta.get('image', '')

    def get_trailer(self, response):
        return response.meta.get('trailer', '')

    def get_duration(self, response):
        runtime = response.xpath(self.get_selector_map('duration')).get()
        if runtime:
            runtime = re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})', runtime)
            if runtime:
                hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
                return str(hours * 3600 + minutes * 60 + seconds)
        return None
