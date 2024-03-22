import string
import time
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLifeSelectorSpider(BaseSceneScraper):
    name = 'LifeSelector'
    network = 'Life Selector'
    parent = 'Life Selector'
    site = 'Life Selector'

    start_urls = [
        'https://lifeselector.com',
    ]

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # ~ 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # ~ 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            # ~ 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/game/listGames?format=partial&offset=%s&gameType=all&order=releaseDate&_=%s'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request("https://lifeselector.com", callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 20)
        timestamp = str(int(time.time()))
        return self.format_url(base, self.get_selector_map('pagination') % (page, timestamp))

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "episodeBlock") and contains(@class, "notOrdered")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('./div/h3[@class="game-title"]/text()').get())
            item['description'] = ""
            description = scene.xpath('.//div[@class="story"]//text()')
            if description:
                item['description'] = " ".join(list(map(lambda x: x.strip(), description.getall()))).strip().replace("\n", "").replace("\t", "").replace("\r", "")
            item['date'] = ''
            item['image'] = ""
            item['image_blob'] = ""
            image = scene.xpath('./a[1]/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                if "list/soft/1.jpg" in item['image']:
                    item['image'] = item['image'].replace("list/soft/1", "poster/soft/1_size1200")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            performers = scene.xpath('.//div[@class="models"]/a/text()')
            item['performers'] = []
            if performers:
                item['performers'] = performers.getall()
            tags = scene.xpath('.//div[@class="tags"]/a/text()')
            item['tags'] = []
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.getall()))
            item['trailer'] = ''
            trailer = scene.xpath('.//div[contains(@class,"action")]/button[contains(@class, "trailer")]/@data-video-src')
            if trailer:
                item['trailer'] = self.format_link(response, trailer.get())
            item['id'] = scene.xpath('./@id').get()
            item['network'] = "Life Selector"
            item['parent'] = "Life Selector"
            item['site'] = "Life Selector"
            item['url'] = self.format_link(response, scene.xpath('./a[1]/@href').get())
            yield self.check_item(item, self.days)
