import scrapy
import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkKinkPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'external_id': r'model/(.*)/'
    }

    name = 'KinkPerformer'
    network = 'Kink'

    start_url = 'https://www.kink.com'

    paginations = [
        '/models?genderIds=woman&sort=latestActivity&page=%s',
        '/models?genderIds=man&sort=latestActivity&page=%s',
        '/models?genderIds=tswoman&sort=latestActivity&page=%s',
        '/models?genderIds=nonbinary&sort=latestActivity&page=%s',
        '/models?genderIds=tsman&sort=latestActivity&page=%s',
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
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    async def start(self):
        meta = {}
        meta['playwright'] = True
        for pagination in self.paginations:
            meta['pagination'] = pagination
            meta['page'] = self.page
            link = self.start_url
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = self.copy_meta(response)
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                url=self.get_next_page_url(response.url, meta['page'], meta['pagination'])
                print(f'NEXT PAGE: {str(meta["page"])}  ({url})')
                yield scrapy.Request(url, callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_gender(self, pagination):
        if "=woman" in pagination:
            return 'Female'
        if "=man" in pagination:
            return 'Male'
        if "=tswoman" in pagination:
            return 'Trans Female'
        if "=tsman" in pagination:
            return 'Trans Male'
        if "=nonbinary" in pagination:
            return 'Non Binary'        
        return ""

    def get_performers(self, response):
        meta = self.copy_meta(response)
        performers = response.xpath('//div[@class="col"]/div[contains(@class, "position-relative")]')
        for performer in performers:
            item = self.init_performer()
            perf_id = performer.xpath('./div[contains(@class, "favorite-button")]/@data-id').get()
            perf_name = self.cleanup_title(performer.xpath('./span[contains(@class, "d-block")]/span[contains(@class, "text-white")]/text()').get())
            if " " not in perf_name:
                perf_name = perf_name + " " + perf_id
            item['name'] = perf_name
            image = performer.xpath('./a/img/@data-src')
            if not image:
                image = performer.xpath('./a/img/@src')
            if image:
                image = image.get()
                if "missing-image" not in image.lower() and  "missing-model" not in image.lower():
                    item['image'] = self.format_link(response, image)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                    if "?" in item['image']:
                        item['image'] = re.search(r'(.*)\?', item['image']).group(1)
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())
            item['network'] = "Kink"
            item['gender'] = self.get_gender(meta['pagination'])
            yield item
