import re

import scrapy
from scrapy_playwright.page import PageMethod

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLustRealitySpider(BaseSceneScraper):
    name = 'LustReality'
    network = 'LustReality'
    parent = 'LustReality'
    site = 'LustReality'

    start_urls = [
        'https://www.lustreality.com',
    ]

    # The site sits behind Anubis (techaro.lol), a proof-of-work anti-bot. It is
    # NOT Cloudflare, which is why FlareSolverr is no help -- it reports
    # "Challenge not detected" and still receives the block. Plain requests get
    # an 8.8KB "Making sure you're not a bot!" page for every URL.
    #
    # Anubis's challenge is solved in JavaScript, so a real browser clears it
    # unaided: Playwright renders the listing in under five seconds and mints the
    # techaro.lol-anubis-auth cookie itself. Hand-copied cookies work too, but
    # that JWT expires after about a week and would need re-pasting every time,
    # so the browser does it instead.
    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 2,
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 90000,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    cookies = [
        {"name": "av_", "value": "true", "domain": ".lustreality.com", "path": "/"},
    ]

    # The tour was rebuilt behind that wall: scenes moved from a numeric
    # "...-<id>.htm" URL to a bare /en/<slug>, so the old external_id regex
    # matched nothing, and every rightWrapper selector is gone. The site now
    # publishes only a relative age ("yesterday", "2 weeks ago") rather than a
    # release date, so date is left empty for TPDB to use the import date rather
    # than invent a precise-looking one that would be wrong for the back
    # catalogue.
    selector_map = {
        'title': '//h1//text()',
        'description': '//div[contains(@class, "video-detail__description")]//text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//a[contains(@class, "video-actor-tag")]//text()',
        'tags': '//a[contains(@class, "video-tag")]/text()',
        'external_id': r'/en/([a-z0-9-]+)$',
        'pagination': '/en/videos?page=%s',
        'type': 'Scene',
    }

    async def start(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'playwright': True,
                                       # Anubis solves its challenge and reloads
                                       # after the initial load event, so the
                                       # cards are not there yet when the page
                                       # first settles -- wait for them.
                                       'playwright_page_methods': [
                                           PageMethod('wait_for_selector', 'a.video-card')]},
                                 headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        for card in response.xpath('//a[contains(@class, "video-card")]'):
            link = card.xpath('./@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue
            # Only the card carries the runtime; the scene page shows it too but
            # in a meta strip shared with the view counter.
            runtime = card.xpath('.//div[contains(@class, "video-card__duration")]/text()').get()
            scene_meta = dict(meta)
            if runtime:
                scene_meta['duration'] = self.duration_to_seconds(runtime.strip())
            scene_meta['playwright'] = True
            scene_meta['playwright_page_methods'] = [PageMethod('wait_for_selector', 'h1')]
            yield response.follow(link, callback=self.parse_scene, meta=scene_meta)

    def get_tags(self, response):
        # Rendered as "#Brunette", "#Small boobs".
        tags = []
        for tag in super().get_tags(response):
            tag = tag.lstrip('#').strip()
            if tag and tag not in tags:
                tags.append(tag)
        return tags
