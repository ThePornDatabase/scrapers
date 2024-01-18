import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkKinkSpider(BaseSceneScraper):
    name = 'KinkPlaywright'
    network = "Kink"

    url = 'https://www.kink.com'

    paginations = [
        '/search?type=shoots&thirdParty=false&sort=published&page=%s',
        # ~ '/search?type=shoots&sort=published&featuredIds=%s',
        # ~ '/search?type=shoots&sort=published&thirdParty=true&page=%s',
        # ~ '/search?type=shoots&sort=published&channelIds=wasteland&sort=published&page=%s',
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

    selector_map = {
        'title': '//title/text()',
        'description': '//span[@class="description-text"]/p/text()|//h4[contains(text(), "Description")]/following-sibling::span[1]/p/text()',
        'date': "//span[@class='shoot-date']/text()",
        'image': '//meta[@name="twitter:image"]/@content|//video/@poster',
        'duration': '//span[@class="clock"]/text()',
        'performers': '//p[@class="starring"]/span/a/text()|//span[contains(@class, "text-primary fs-5")]/a[contains(@href, "/model/")]/text()',
        'tags': '//a[@class="tag"]/text()|//h4[contains(text(), "Categories")]/following-sibling::span[1]/a/text()',
        'external_id': r'/shoot/(\d+)',
        'trailer': '//meta[@name="twitter:player"]/@content|//div[contains(@class,"kvjs-container")]/@data-setup',
        're_trailer': r'trailer.*?quality.*?(http.*?)[\'\"]',
        'pagination': '/shoots/latest?page=%s'
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
        yield scrapy.Request("https://www.kink.com", callback=self.start_requests2, headers=self.headers, cookies=self.cookies, meta={"playwright": True})

    def start_requests2(self, response):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta={'page': self.page, 'pagination': pagination, "playwright": True}, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath("//a[@class='shoot-link']/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return response.xpath('//div[@class="shoot-page"]/@data-sitename|//div[contains(@class, "shoot-detail-legend")]/span/a/text()').get().strip()

    def get_performers(self, response):
        performers = super().get_performers(response)
        return list(map(lambda x: string.capwords(x.strip(",").strip().lower()), performers))

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = list(map(lambda x: string.capwords(x.strip(",").strip().lower()), tags))
        tags = list(filter(None, tags))
        return tags

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def parse_scene(self, response):
        item = SceneItem()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['markers'] = self.get_markers(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.network
        item['parent'] = self.get_site(response)
        item['type'] = 'Scene'

        matches = ['str8hell', 'cfnmeu', 'malefeet4u', 'williamhiggins', 'ambushmassage', 'swnude', 'sweetfemdom']
        if not any(x in item['site'] for x in matches):
            yield self.check_item(item, self.days)

    def get_date(self, response):
        scenedate = response.xpath('//div[contains(@class,"kvjs-container")]/@data-setup')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = re.search(r'publishedDate.*?(\d{4}-\d{2}-\d{2})', scenedate)
            if scenedate:
                return scenedate.group(1)
        return ''
