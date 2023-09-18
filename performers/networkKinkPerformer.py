import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkKinkPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',


        'external_id': r'model/(.*)/'
    }

    name = 'KinkPerformer'
    network = 'Kink'

    start_url = 'https://www.kink.com'

    paginations = [
        '/search?type=performers&genderIds=woman&sort=latestActivity&page=%s',
        '/search?type=performers&genderIds=man&sort=latestActivity&page=%s',
        '/search?type=performers&genderIds=tswoman&sort=latestActivity&page=%s',
        '/search?type=performers&genderIds=nonbinary&sort=latestActivity&page=%s',
        '/search?type=performers&genderIds=tsman&sort=latestActivity&page=%s',
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
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
        meta['playwright'] = True
        for pagination in self.paginations:
            meta['pagination'] = pagination
            link = self.start_url
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_gender(self, pagination):
        if "=woman" in pagination:
            return 'Female'
        if "=man" in pagination:
            return 'Male'
        if "=ts" in pagination or "=non" in pagination:
            return 'Trans'
        return ""

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()
            item['name'] = self.cleanup_title(performer.xpath('.//a[@class="model-name"]/text()').get())
            item['url'] = self.format_link(response, performer.xpath('.//a[@class="model-name"]/@href').get())
            image = performer.xpath('.//img/@src')
            item['image'] = ""
            item['image_blob'] = ""
            if image:
                image = image.get()
                if "missing-image" not in image:
                    item['image'] = self.format_link(response, image)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['network'] = "Kink"
            item['gender'] = self.get_gender(meta['pagination'])
            item['bio'] = None
            item['astrology'] = None
            item['birthday'] = None
            item['birthplace'] = None
            item['ethnicity'] = None
            item['eyecolor'] = None
            item['haircolor'] = None
            item['height'] = None
            item['measurements'] = None
            item['cupsize'] = None
            item['nationality'] = None
            item['piercings'] = None
            item['tattoos'] = None
            item['weight'] = None
            item['fakeboobs'] = None

            yield item
