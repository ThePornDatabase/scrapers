import re
import json
import string
import scrapy
from scrapy_playwright.page import PageMethod
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class NetworkKinkSpider(BaseSceneScraper):
    name = 'KinkPlaywright'
    network = "Kink"

    url = 'https://www.kink.com'

    # No hardcoded cookies — Playwright manages the session via its browser context.
    # The age-gate click in start_requests creates a fresh server-side session each run.
    cookies = []


    paginations = [
        '/shoots?thirdParty=false&sort=published&page=%s',
        # ~ '/search?type=shoots&sort=published&featuredIds=%s',
        # ~ '/search?type=shoots&sort=published&thirdParty=true&page=%s',
        # ~ '/shoots?channelIds=behindkink&thirdParty=false&sort=published&page=%s',
        # ~ '/shoots?channelIds=boundgangbangs&thirdParty=false&sort=published&page=%s',
        # '/shoots?channelIds=filthyfemdom&thirdParty=true&sort=published&page=%s',
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
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
        'description': '//span[contains(text(), "Description:")]/following-sibling::span[1]//text()',
        'date': '//span[@class="shoot-date"]/text()|//div[contains(@class, "shoot-detail-legend")]/span[contains(@class, "text-muted")]/text()',
        'image': '//meta[@name="twitter:image"]/@content|//video/@poster|//a[contains(@class, "ratio-poster")]/img/@src',
        'duration': '//span[@class="clock"]/text()',
        'performers': '//p[@class="starring"]/span/a/text()|//span[contains(@class, "text-primary fs-5")]/a[contains(@href, "/model/")]/text()',
        # ~ 'tags': '//a[@class="tag"]/text()|//h4[contains(text(), "Categories")]/following-sibling::span[1]/a/text()',
        'tags': '//div[contains(@class, "shoot-detail-description")]//a[contains(@href, "/tag/")]/text()',
        'external_id': r'/shoot/(\d+)',
        'trailer': '//meta[@name="twitter:player"]/@content|//div[contains(@class,"kvjs-container")]/@data-setup',
        're_trailer': r'trailer.*?quality.*?(http.*?)[\'\"]',
        'pagination': '/shoots/latest?page=%s'
    }

    custom_scraper_settings = {
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
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ],
        },
        'PLAYWRIGHT_CONTEXTS': {
            'default': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
                'locale': 'en-US',
                'timezone_id': 'America/New_York',
                'viewport': {'width': 1920, 'height': 1080},
            },
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,
    }

    async def start(self):
        meta = {
            'playwright': True,
            'page': self.page,
            'dont_merge_cookies': True,  # let Playwright's browser context manage cookies, not Scrapy
            'playwright_page_methods': [
                PageMethod('wait_for_load_state', 'domcontentloaded'),
                PageMethod('wait_for_timeout', 3000),
                # Conditionally click the age gate — JS no-op if not present
                PageMethod('evaluate', 'document.getElementById("enter-actual-site")?.click()'),
                PageMethod('wait_for_load_state', 'domcontentloaded'),
                PageMethod('wait_for_timeout', 3000),
            ],
        }
        yield scrapy.Request("https://www.kink.com", callback=self.start_requests2, headers=self.headers, meta=meta)

    def start_requests2(self, response):
        meta = dict(response.meta)
        # Click-through is only needed on the first request — strip it for downstream
        meta.pop('playwright_page_methods', None)
        for pagination in self.paginations:
            link = self.get_next_page_url(self.url, self.page, pagination)
            meta['pagination'] = pagination
            yield scrapy.Request(link, callback=self.parse, meta=meta)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = self.copy_meta(response)
                    meta['page'] = meta['page'] + 1
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "shoot-thumbnail")]/ancestor::div[@class="col"]')
        for scene in scenes:
            parse_scene = True
            scenedate = scene.xpath('.//small/span[contains(text(), ",")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
                meta['date'] = scenedate
                if not self.check_item(meta, self.days):
                    parse_scene = False

            scene = scene.xpath('.//a[contains(@class, "d-block")]/img/../@href').get()
            meta['id'] = re.search(self.get_selector_map('external_id'), scene).group(1)
            if meta['id'] and parse_scene:
                url = self.format_url(response.url, scene)
                yield scrapy.Request(url, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return response.xpath('//div[@class="shoot-page"]/@data-sitename|//div[contains(@class, "shoot-detail-legend")]/span/a/text()').get().strip()

    def get_performers(self, response):
        performers = []
        perf_list = response.xpath('//script[contains(@type, "json") and contains(text(), "actor")]/text()')
        if perf_list:
            perf_list = json.loads(perf_list.get())
            for performer in perf_list['actor']:
                if 'assorted cast' not in performer['name'].lower():
                    perf_name = performer['name']
                    perf_id = re.search(r'model/(\d+)', performer['url']).group(1)
                    if " " not in perf_name:
                        perf_name = perf_name + " " + perf_id
                    performers.append(perf_name)
        performers = list(map(lambda x: string.capwords(x.strip(",").strip().lower()), performers))
        return performers

    def get_director(self, response):
        director = None
        dir_list = response.xpath('//script[contains(@type, "json") and contains(text(), "director")]/text()')
        if dir_list:
            dir_list = json.loads(dir_list.get())
            if "director" in dir_list and dir_list['director']:
                if 'assorted cast' not in dir_list['director']['name'].lower():
                    director = string.capwords(dir_list['director']['name'])
        return director
    
    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = list(map(lambda x: string.capwords(x.strip(",").strip().lower()), tags))
        tags = list(filter(None, tags))
        return tags

    def get_next_page_url(self, url, page, pagination):
        url = self.format_url(url, pagination % page)
        return url

    def parse_scene(self, response):

        local_run = self.settings.get('local')
        show_blob = self.settings.get('showblob')
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        meta = self.copy_meta(response)
        item = self.init_scene()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        if not item['site']:
            item['site'] = self.network
        item['date'] = self.get_date(response)
        item['director'] = self.get_director(response)
        item['image'] = self.get_image(response)
        if item['image']:
            if (not force_update or (force_update and "image" in force_fields)) and (not local_run or (local_run and show_blob)):
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if "&amp" in item['image']:
                item['image'] = re.search(r'(.*?)\&amp', item['image']).group(1)
            if "&s" in item['image']:
                item['image'] = re.search(r'(.*?)\&s', item['image']).group(1)
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
        if not scenedate:
            scenedate = response.xpath('//div[contains(@class, "shoot-detail-legend")]/span[contains(@class, "text-muted")]/text()')
            if scenedate:
                scenedate = self.parse_date(scenedate.get()).strftime('%Y-%m-%d')
                if scenedate:
                    return scenedate
        return ''

    def get_title(self, response):
        title = super().get_title(response)
        if "|" in title:
            title = re.search(r'(.*?)\|', title).group(1)
        return title.strip()
