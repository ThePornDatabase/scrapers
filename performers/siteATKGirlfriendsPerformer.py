import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
false = False
true = True


class SiteATKGirlfriendsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[contains(@class, "page-title")]/text()',
        'image': '//div[contains(@class, "image-wrap")]/img/@src',
        'image_blob': True,
        'cupsize': '//div[contains(@class, "image-wrap")]//b[contains(text(), "Bust")]/following-sibling::text()[1]',
        'ethnicity': '//div[contains(@class, "image-wrap")]//b[contains(text(), "Ethnicity")]/following-sibling::text()[1]',
        'haircolor': '//div[contains(@class, "image-wrap")]//b[contains(text(), "Hair")]/following-sibling::text()[1]',
        'height': '//div[contains(@class, "image-wrap")]//b[contains(text(), "Height")]/following-sibling::text()[1]',
        'weight': '//div[contains(@class, "image-wrap")]//b[contains(text(), "Weight")]/following-sibling::text()[1]',
        'pagination': '/tour/lmodels?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'ATKGirlfriendsPerformer'
    network = 'ATKingdom'

    custom_settings = {'CONCURRENT_REQUESTS': 1}
    start_urls = ['https://www.atkgirlfriends.com']
    headers = {'referer': 'https://www.atkgirlfriends.com'}

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

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request("https://www.atkgirlfriends.com", callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class,"model-profile-wrap")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = weight.replace(" ", "")
        weight = weight.replace("lbslbs", "lbs")
        return weight
