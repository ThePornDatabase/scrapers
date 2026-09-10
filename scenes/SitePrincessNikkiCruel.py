import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePrincessNikkiCruelSpider(BaseSceneScraper):
    name = 'PrincessNikkiCruel'
    network = 'Princess Nikki Cruel'
    parent = 'Princess Nikki Cruel'
    site = 'Princess Nikki Cruel'

    # shop.princessnikkicruel.com no longer resolves at all -- the shop was folded
    # into the main site, which was rebuilt on Livewire.  The collection pages and
    # their div.collection cards are gone; scenes are /movie/<id>/<slug> now and the
    # listing is /movies.  Its ?page= parameter is handled client-side and always
    # returns the same 32 newest, so there is one listing page.
    start_urls = [
        'https://princessnikkicruel.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "movieTitle")]/h1/text()',
        # The synopsis is a bare text node sitting between the release line and the
        # cast links, with no element of its own to address.
        'description': '//div[contains(@class, "movieMeta")]//div[contains(@class, "mb-3")]/following-sibling::text()',
        'date': '//div[contains(@class, "movieMeta")]//text()[contains(., "Released on")]',
        're_date': r'Released on:\s*(\d{2}-\d{2}-\d{4})',
        'date_formats': ['%d-%m-%Y'],
        'image': '',
        'performers': '//div[contains(@class, "movieMeta")]//a[contains(@href, "/model/")]/text()',
        'tags': '//div[contains(@class, "movieMeta")]//a[contains(@href, "/movies/category/")]/text()',
        'external_id': r'/movie/(\d+)/',
        'trailer': '',
        'pagination': '/movies',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination'))

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "movieItem")]'):
            link = card.xpath('.//div[contains(@class, "title")]/a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            # The scene page only carries numbered screenshots; the card holds the
            # artwork still.
            image = card.xpath('.//img/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        return response.meta.get('image', '')
