import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SieTeenyTabooSpider(BaseSceneScraper):
    name = 'TeenyTaboo'
    network = 'Teeny Taboo'
    parent = 'Teeny Taboo'
    site = 'Teeny Taboo'

    start_urls = [
        'https://www.teenytaboo.com',
    ]

    # ~ cookies = [{"name": "warn", "value": "true"}]
    cookies = [{"domain":".teenytaboo.com","expirationDate":1781966799.731742,"hostOnly":false,"httpOnly":false,"name":"_ga","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"GA1.1.1321320240.1747406374"},{"domain":".teenytaboo.com","expirationDate":1781967409.431503,"hostOnly":false,"httpOnly":false,"name":"_ga_JX9WTNWZ9D","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"GS2.1.s1747406373$o1$g1$t1747407409$j0$l0$h0"},{"domain":"teenytaboo.com","hostOnly":true,"httpOnly":false,"name":"PHPSESSID","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"anvo6alorj9kr570llt2997amh"},{"domain":"teenytaboo.com","expirationDate":1753191987,"hostOnly":true,"httpOnly":false,"name":"warn","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"true"}]

    selector_map = {
        'title': '//h1[contains(@class, "customhcolor")]/text()',
        'description': '//h2[contains(@class, "customhcolor")]/p/text()',
        'date': '//span[@class="date"]/text()',
        'date_formats': ['%B %d %Y'],
        'image': '//center/img/@src',
        'image_blob': True,
        'performers': '//h3[contains(@class, "customhcolor")]/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'video/(.*?)/',
        'pagination': '/page%s'
    }

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        # ~ 'AUTOTHROTTLE_ENABLED': True,
        # ~ 'AUTOTHROTTLE_START_DELAY': 1,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        # 'DOWNLOAD_DELAY': 60,
        # 'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'SPIDERMON_ENABLED': False,
        'DOWNLOAD_FAIL_ON_DATALOSS': True,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 408, 307, 403],
        'HANDLE_HTTPSTATUS_LIST': [500, 503, 504, 400, 408, 307, 403],
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 300,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 301,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 100,
        }
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"videoimg_wrapper")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                url=self.format_link(response, scene)
                yield scrapy.Request(url, callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        return string.capwords(title.replace("-", " "))

    def get_tags(self, response):
        tags = response.xpath('//h4[contains(@class, "customhcolor")]/text()')
        if tags:
            tags = tags.get().split(",")
            return list(map(lambda x: string.capwords(x.strip()), tags))
        return []
