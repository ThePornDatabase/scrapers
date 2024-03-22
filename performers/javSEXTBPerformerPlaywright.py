import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class JavSEXTBPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-user")]/following-sibling::span/a/text()',
        'image': '//section[@class="tray all"]/div/img/@data-src',
        'image_blob': True,
        'birthday': '//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-birthday")]/following-sibling::span/text()',
        'height': '//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-arrows-alt") and contains(following-sibling::text(), "Height")]/following-sibling::span/text()',
        'measurements': 'InCode',

        'pagination': '/list-actress/pg-%s',
        'external_id': r'model/(.*)/'
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': False,
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

    name = 'JAVSEXTBPerformerPlaywright'
    network = 'R18'

    start_urls = [
        'https://sextb.net',
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = response.meta
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="tray-item-actress"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_measurements(self, response):
        bust = response.xpath('//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-arrows-alt") and contains(following-sibling::text(), "Breast")]/following-sibling::span/text()')
        waist = response.xpath('//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-arrows-alt") and contains(following-sibling::text(), "Waist")]/following-sibling::span/text()')
        hips = response.xpath('//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-arrows-alt") and contains(following-sibling::text(), "Hips")]/following-sibling::span/text()')

        if bust and waist and hips:
            bust = re.search(r'(\d+)', bust.get())
            if bust:
                bust = bust.group(1)
            waist = re.search(r'(\d+)', waist.get())
            if waist:
                waist = waist.group(1)
            hips = re.search(r'(\d+)', hips.get())
            if hips:
                hips = hips.group(1)
            if bust and waist and hips:
                if bust:
                    bust = round(int(bust) / 2.54)
                if waist:
                    waist = round(int(waist) / 2.54)
                if hips:
                    hips = round(int(hips) / 2.54)

                if bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        bust = response.xpath('//div[contains(@class,"actor-info")]/ul/li/i[contains(@class, "fa-arrows-alt") and contains(following-sibling::text(), "Breast")]/following-sibling::span/text()')
        if bust:
            bust = re.search(r'(\d+)', bust.get())
            if bust:
                bust = bust.group(1)
                if bust:
                    bust = round(int(bust) / 2.54)
                if bust:
                    return str(bust)
        return ''

    def get_name(self, response):
        name = super().get_name(response)
        if "(" in name:
            name = re.search(r'(.*?)\(', name).group(1)
        return string.capwords(name.strip())

    def get_height(self, response):
        height = super().get_height(response)
        return height.replace(" ", "")
