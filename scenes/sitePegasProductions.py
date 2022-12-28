import re
import string
import unicodedata
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class SitePegasProductionsSpider(BaseSceneScraper):
    name = 'PegasProductions'
    network = 'Pegas Productions'
    parent = 'Pegas Productions'
    site = 'Pegas Productions'

    start_urls = [
        'https://www.pegasproductions.com',
    ]

    cookies = {
        'langue': 'en',
        'consent': 'true',
        'Niche': 'Pegas',
        'AB': 'B',
        'limiteouvert': '0'
    }

    # ~ custom_settings = {'USE_PROXY': 'True'}

    selector_map = {
        'title': '//div[@class="span10"]/h4/text()',
        'description': '//div[@class="span10"]//h5/following-sibling::p[1]/text()',
        'date': '//div[@id="date-duree"]/div[1]/p/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//script[contains(text(), "poster")]/text()',
        're_image': r'(http.*?\.jpg)',
        'performers': '//p[contains(text(), "STARRING")]/following-sibling::div[@class="span5"]//h4/text()',
        'tags': '//div[@class="span9"]/h4/strong[contains(text(), "Tags")]/following-sibling::text()',
        'external_id': r'\.com/(.*)\?',
        'trailer': '//script[contains(text(), "poster")]/text()',
        're_trailer': r'(http.*?\.mp4)',
        'pagination': '/videos-porno-tour/page/%s?langue=en'
    }

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 100,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    def start_requests(self):
        settings = get_project_settings()

        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        meta = {}
        meta['playwright'] = True
        meta['page'] = self.page
        if 'USE_PROXY' in self.settings.attributes.keys():
            use_proxy = self.settings.get('USE_PROXY')
        elif 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)
                                     
    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//span[contains(text(), "Latest") and not(contains(text(), "Girls"))]/following-sibling::div//div[@class="rollover_img_videotour"]/a/@href|//span[contains(text(), "Récentes") and not(contains(text(), "Filles"))]/following-sibling::div//div[@class="rollover_img_videotour"]/a/@href').getall()
        # ~ scenes = response.xpath('//span[contains(text(), "Récentes") and not(contains(text(), "Filles"))]/following-sibling::div//div[@class="rollover_img_videotour"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                if "&nats=" in scene:
                    scene = re.search(r'(.*)&nats=', scene).group(1)
                scene = scene.replace("?langue=fr", "?langue=en")
                if "?langue=en" not in scene:
                    scene = scene + "?langue=en"
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = response.xpath(self.get_selector_map('tags')).get()
        tags = tags.split(",")
        tags = list(map(lambda x: x.strip().title(), tags))
        tags = [i for i in tags if i]
        return tags

    def get_title(self, response):
        title = super().get_title(response)
        return self.strip_accents(title)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(map(lambda x: self.strip_accents(x), performers))
        return performers

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except (TypeError, NameError):  # unicode is a default on python 3
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        text = re.sub('[^0-9a-zA-Z ]', '', text)
        return string.capwords(str(text))

    def get_image(self, response):
        image = super().get_image(response)
        if "jpg" not in image:
            image = response.xpath('//meta[@itemprop="thumbnailUrl"]/@content').get()
            image = image.replace("screenshots", "screenshots/")
        return image
