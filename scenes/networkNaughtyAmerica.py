import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NaughtyAmericaSpider(BaseSceneScraper):
    name = 'NaughtyAmerica'
    network = 'Naughty America'
    parent = 'Naughty America'

    start_urls = [
        'https://www.naughtyamerica.com'
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[contains(@class, "synopsis grey-text")]/span/following-sibling::text()|//div[contains(@class, "synopsis grey-text")]/text()',
        'date': '//div[@class="date-tags"]/span[contains(@class,"entry-date")]/text()',
        'image': '//a[@class="play-trailer"]/picture//img/@data-srcset',
        'performers': '//a[@class="scene-title grey-text link"]/text()',
        'tags': '//a[@class="cat-tag"]/text()',
        'external_id': '(\\d+)$',
        'trailer': '',
        'pagination': '/new-porn-videos?page=%s'
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

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath(
            '//div[@class="scene-grid-item"]/a[contains(@href,"/scene/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath(
            '//a[@class="play-trailer"]/picture[1]//source[contains(@data-srcset,"jpg")]/@data-srcset').get()
        if not image:
            image = response.xpath(
                '//dl8-video/@poster[contains(.,"jpg")]').get()

        if image[0:2] == "//":
            image = "https:" + image

        return self.format_link(response, image)

    def get_site(self, response):
        site = response.xpath(
            '//div[@class="scene-info"]//a[contains(@class,"site-title")]/text()').get()
        if site:
            return site.strip()
        return super().get_site(response)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="date-tags"]/span[contains(@class,"entry-date")]/following-sibling::div/text()[contains(., "min")]')
        if duration:
            duration = re.search(r'(\d+) min', duration.get()).group(1)
            duration = str(int(duration) * 60)
        return duration
