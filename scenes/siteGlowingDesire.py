import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGlowingDesireSpider(BaseSceneScraper):
    name = 'GlowingDesire'
    network = 'Glowing Desire'
    parent = 'Glowing Desire'
    site = 'Glowing Desire'
    start_url = 'https://glowingdesire.com'

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@class="content"]/p//text()',
        'date': '//span[@class="date"]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//video/@poster',
        'performers': '//div[contains(@class, "content-pane-performers")]/a/text()',
        'tags': '//div[contains(@class, "categories")]/a/text()',
        'external_id': r'stream/(\d+)/',
        'pagination': '/video/gallery/%s',
        'type': 'Scene',
    }

    async def start(self):
        meta = {}
        meta['playwright'] = True
        meta['page'] = self.page
        link = self.start_url
        yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return self.format_url(base, '/video/gallery/')
        else:
            page = str((int(page) - 1) * 12)
            return self.format_url(base, f'/video/gallery/{page}/')
        
    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "overlay-item")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
