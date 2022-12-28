import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
false = False
true = True


class SiteReidMyLipsSpider(BaseSceneScraper):
    name = 'ReidMyLips'
    network = 'Andomark'
    parent = 'Reid My Lips'
    site = 'Reid My Lips'

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
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # ~ 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            # ~ 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    cookies = {
        'SPSI': '',
    }    

    start_urls = [
        'https://reidmylips.elxcomplete.com',  # Will requires bypass
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'date': '//span[@class="availdate"]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'description': '//span[contains(@class,"description")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.+)\.html',
        'trailer': '//a[@class="update_image_big"]/@onclick',
        're_trailer': r'\'(.*.mp4)\'',
        'pagination': '/categories/movies_%s_d.html'
    }

    def start_requests2(self, response):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta={'page': self.page, 'pagination': pagination, "playwright": True}, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if len(scene) > 10:
                yield scrapy.Request(url=scene, callback=self.parse_scene,
                                     cookies=self.cookies)
