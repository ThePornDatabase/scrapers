import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWhornyFilmsPlaywrightSpider(BaseSceneScraper):
    name = 'WhornyFilmsPlaywright'
    network = 'Whorny Films'
    parent = 'Whorny Films'
    site = 'Whorny Films'

    start_urls = [
        'https://whornyfilms.com',
    ]

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
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    selector_map = {
        'title': '//h1[contains(@class,"elementor-heading-title")]/text()|//meta[@property="og:image:alt"]/@content',
        'description': '',
        'date': '//meta[@property="article:published_time"]/@content|//meta[@property="og:updated_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class, "gallery-item-6")]/div/a/div/img/@data-lazy-src|//meta[@property="og:image"]/@content',
        'performers': '//div[@data-id="501b355"]/div//ul/li/a/text()',
        'tags': '//meta[@property="article:tag"]/@content',
        'duration': '//div[@data-id="4cf1341"]/div/h2/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/blog/2021/08/04/search-and-filter/?sf_data=results&sf_paged=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        yield scrapy.Request("https://whornyfilms.com", callback=self.start_requests2, headers=self.headers, cookies=self.cookies, meta={"playwright": True})

    def start_requests2(self, response):
        meta = response.meta
        for link in self.start_urls:
            url = self.get_next_page_url(link, self.page)
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"dce-item")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[@data-id="501b355"]/div//ul/li/a/text()')
        if performers:
            performers = performers.getall()
        performers2 = []
        for performer in performers:
            if not performer.isupper():
                performers2.append(performer)
        return performers2
