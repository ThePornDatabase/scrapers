import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCitebeur(BaseSceneScraper):
    name = 'Citebeur'
    site = 'Citebeur'
    parent = 'Citebeur'
    network = 'Citebeur'

    start_urls = ['https://www.citebeur.com']

    selector_map = {
        'title': '//div[contains(@class, "col-12 text-center")]/h1/text()',
        'description': '//div[contains(@class, "col-12")]/h2/text()',
        'date': '',
        'image': '//div[contains(@class, "d-block embed-responsive embed-responsive-16by9 mb-2 rounded ")]/img/@src',
        'performers': '//i[contains(@class,"fa-star ")]/following-sibling::text()',
        'tags': '//div[contains(@class, "col-12 text-center px-4 py-2")]/a/h3/text()',
        'external_id': r'detail/(\d+)-',
        'trailer': '//video[contains(@class, "embed-responsive-item obj-cover d-none")]/source/@src',
        'pagination': '/en/videos?page=%s'
    }

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
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        page = str(int(page) -1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"video-gallery")]/a[contains(@href, "en/videos/detail")][1]/@href|//div[@class="position-relative"]/a[contains(@href, "en/videos/detail")][1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//span[@class="mx-1" and contains(text(), "Time")]/text()')
        if duration:
            duration = duration.get()
            duration = "".join(duration).replace("\n", "").replace("\t", "").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None
