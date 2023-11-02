import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNastyDaddySpider(BaseSceneScraper):
    name = 'NastyDaddy'
    network = 'Nasty Daddy'
    parent = 'Nasty Daddy'
    site = 'Nasty Daddy'

    start_urls = [
        'https://nastydaddy.com',
    ]

    max_retries = 3

    cookies = {'warn': '1', 'promocookie': '1', 'ex_referrer': 'https%3A%2F%2Fnastydaddy.com%2Ftour%2Fcategories%2Fmovies.html'}

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        # ~ 'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        # ~ 'AUTOTHROTTLE_START_DELAY': 1,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        # ~ 'DOWNLOAD_DELAY': 2,
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
        },
        'RETRY_HTTP_CODES': [302, 500, 502, 503, 504, 522, 524, 408, 429]
    }

    selector_map = {
        'title': '//div[@class="panel-heading"]/h3/text()',
        'description': '//div[@class="video-seo-description"]/p[not(@class="lead")]/text()',
        'date': '',
        'image': '//video[@id="mediabox"]/@poster',
        'performers': '//span[@class="update_models"]/a/text()',
        'tags': '//div[@class="panel-body"]//a[contains(@href, "categories")]/span/text()',
        'duration': '//div[@class="panel-body"]//h4[contains(text(), "min")]/text()',
        're_duration': r'(\d+)',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        meta['handle_httpstatus_list'] = [302]
        yield scrapy.Request("https://nastydaddy.com/tour/categories/movies.html", callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"show-first")]/a[1]')
        for scene in scenes:
            image = scene.xpath('./img/@data-src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scene = scene.xpath('./@href').get()
            meta['id'] = re.search(r'.*/(.*?)\.htm', scene).group(1)
            meta['url'] = self.format_link(response, scene)
            if meta['id'] and meta['url']:
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = super().get_duration(response)
        if duration:
            duration = str(int(duration) * 60)
        return duration

    def parse_scene(self, response):
        meta = response.meta
        if "signup" in response.url:
            print(f"Retrying {meta['url']}")
            yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta, dont_filter=True)
        else:
            item = SceneItem()
            item['title'] = self.get_title(response)
            item['description'] = self.get_description(response)
            item['site'] = self.get_site(response)
            item['date'] = self.get_date(response)
            item['image'] = response.meta['image']
            item['image_blob'] = response.meta['image_blob']
            item['performers'] = self.get_performers(response)
            item['tags'] = self.get_tags(response)
            item['markers'] = self.get_markers(response)
            item['id'] = response.meta['id']
            item['merge_id'] = self.get_merge_id(response)
            item['trailer'] = self.get_trailer(response)
            item['duration'] = self.get_duration(response)
            item['url'] = self.get_url(response)
            item['network'] = self.network
            item['parent'] = self.parent
            item['store'] = self.get_store(response)
            item['director'] = self.get_director(response)
            item['format'] = self.get_format(response)
            item['back'] = self.get_back_image(response)
            item['back'] = None
            item['back_blob'] = None
            item['sku'] = self.get_sku(response)
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
