import scrapy
import time
import datetime
import dateparser
import re
true = True
false = False

from tpdb.BaseSceneScraper import BaseSceneScraper


class PornCZSpider(BaseSceneScraper):
    name = 'PornCZ'
    network = 'PornCZ'
    parent = 'PornCZ'

    start_urls = [
        'https://www.porncz.com',
        # ~ # 'https://www.amateripremium.com',
        # ~ # 'https://www.amateursfrombohemia.com',
        # ~ # 'https://www.boysfuckmilfs.com',
        # ~ # 'https://www.chloelamour.com',
        # ~ # 'https://www.czechanalsex.com',
        # ~ # 'https://www.czechbiporn.com',
        # ~ # 'https://www.czechboobs.com',
        # ~ # 'https://www.czechdeviant.com',
        # ~ # 'https://www.czechescortgirls.com',
        # ~ # 'https://www.czechexecutor.com',
        # ~ # 'https://www.czechgaycity.com',
        # ~ # 'https://www.czechgypsies.com',
        # ~ # 'https://www.czechhitchhikers.com',
        # ~ # 'https://www.czechrealdolls.com',
        # ~ # 'https://www.czechsexcasting.com',
        # ~ # 'https://www.czechsexparty.com',
        # ~ # 'https://www.czechshemale.com',
        # ~ # 'https://www.dellaitwins.com',
        # ~ # 'https://www.dickontrip.com',
        # ~ # 'https://www.fuckingoffice.com',
        # ~ # 'https://www.fuckingstreet.com',
        # ~ # 'https://www.girlstakeaway.com',
        # ~ # 'https://www.hornydoctor.com',
        # ~ # 'https://www.hornygirlscz.com',
        # ~ # 'https://www.hunterpov.com',
        # ~ # 'https://www.ladydee.com',
        # ~ # 'https://www.publicfrombohemia.com',
        # ~ # 'https://www.retroporncz.com',
        # ~ # 'https://www.sexintaxi.com',
        # ~ # 'https://www.sexwithmuslims.com',
        # ~ # 'https://www.susanayn.com',
        # ~ # 'https://www.teenfrombohemia.com',
        # ~ 'https://www.vrporncz.com',
    ]

    cookies = {
        'age_verify': True,
    }

    custom_scraper_settings = {
        # ~ 'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
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
        # ~ 'DOWNLOAD_HANDLERS': {
            # ~ "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            # ~ "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        # ~ },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 300,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 301,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 100,
        }
    }

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'performers': '//div[contains(@class, "video-info")]/div[contains(@class, "mini-avatars")]//img/@title',
        'date': '//meta[@property="video:release_date"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "video-info")]//a[contains(@href, "category=")]/text()',
        'duration': '//meta[@property="video:duration"]/@content',
        'external_id': r'.*/(.*?)$',
        # ~ 'trailer': '//meta[@property="og:video"]/@content',
        'pagination': '/en/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="card-body"]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[contains(@class, "video-logo")]/a/img/@alt').get()
        if site:
            return site.strip().title()
        else:
            site = response.xpath('//meta[@property="video:series"]/@content').get()
            if site:
                return site
        return super().get_site(response)

    def get_network(self, response):
        return "Porn CZ"

    def get_parent(self, response):
        return "Porn CZ"

    def check_item(self, item, days=None):
        if "date" in item and item['date'] < '2025-03-20':
            return None
        return super().check_item(item, days)
