import re
import string

import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLifeSelectorSpider(BaseSceneScraper):
    name = 'LifeSelector'
    network = 'Life Selector'
    parent = 'Life Selector'
    site = 'Life Selector'

    start_urls = [
        'https://lifeselector.com',
    ]

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # ~ 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'/game/(\d+)/',
        'pagination': '/games?page=%s'
    }

    # /game/listGames no longer returns a partial -- it falls through to the full
    # /games page -- and div.episodeBlock.notOrdered is gone with it.  Cards are
    # div.story.thumbnail now and no longer carry the synopsis, so the game page is
    # visited for its og:description.  As before, the site publishes no release
    # date, no tags and no trailer.

    async def start(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, meta['page']), callback=self.parse,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "story") and contains(@class, "thumbnail")]'):
            link = card.xpath('.//a[contains(@href, "/game/")]/@href').get()
            # member-plus cards are rendered blurred with no link at all
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            meta['id'] = re.search(self.get_selector_map('external_id'), link).group(1)
            meta['title'] = self.cleanup_title(
                (card.xpath('.//a[contains(@class, "title")]/text()').get() or '').strip())

            performers = card.xpath('.//div[contains(@class, "actors")]/a/text()').getall()
            meta['performers'] = [x.strip() for x in performers if x.strip()]

            # the srcsets run small to large, so the last one holds the widest crop
            image = ''
            srcsets = card.xpath('.//source/@data-srcset').getall()
            if srcsets:
                candidates = re.findall(r'(https?://\S+?)\s+\dx', srcsets[-1])
                image = candidates[-1] if candidates else ''
            if not image:
                image = card.xpath('.//img/@data-src').get() or ''
            if image:
                meta['image'] = self.format_link(response, image)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_title(self, response):
        title = response.meta.get('title')
        if not title:
            title = self.cleanup_title(response.xpath('//h1//text()').get() or '')
        return title

    def get_description(self, response):
        description = response.xpath('//meta[@property="og:description"]/@content').get() or ''
        return self.cleanup_description(re.sub(r'\s+', ' ', description))

    def get_image(self, response):
        return response.meta.get('image', '')

    def get_performers(self, response):
        """Taken from the card -- the game page lists related models alongside the
        cast, with no way to tell them apart."""
        return response.meta.get('performers', [])

    def get_date(self, response):
        return None

    def get_tags(self, response):
        return []

    def get_trailer(self, response):
        return ''
