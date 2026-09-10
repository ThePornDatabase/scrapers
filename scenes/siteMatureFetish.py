import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMatureFetishSpider(BaseSceneScraper):
    name = 'MatureFetish'
    network = 'Mature NL'
    parent = 'Mature Fetish'
    site = 'Mature Fetish'

    start_urls = [
        'https://maturefetish.com',
    ]

    # /en/content/N 404s.  The listing moved to /en/updates, and its ?page=N is
    # handled client-side (every page returns the same first entry), so the crawl
    # takes the one page it serves.  The scene page is a Svelte app: the synopsis,
    # tags and stats blocks are all rendered in the browser, leaving the h1, the
    # player poster and the model links as the only server-side content.
    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '',
        'image': '//video/@poster',
        'performers': '//a[contains(@href, "/model/")]/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'/update/(\d+)/',
        'pagination': '/en/updates',
        'type': 'Scene',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(url=self.format_url(link, self.get_selector_map('pagination')),
                                 callback=self.parse, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        """The page links each model twice (cast strip and player credits)."""
        names = [x.strip() for x in response.xpath(self.get_selector_map('performers')).getall() if x and x.strip()]
        return list(dict.fromkeys(names))

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # div.grid-tile-content is gone; the cards are div.update wrappers around a
        # direct /en/update/<id>/<slug> link, repeated per card
        scenes = response.xpath('//a[contains(@href, "/update/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
