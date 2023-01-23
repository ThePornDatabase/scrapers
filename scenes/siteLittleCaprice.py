import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class LittleCapriceSpider(BaseSceneScraper):
    name = 'LittleCaprice'
    network = 'Little Caprice Dreams'

    start_urls = [
        'https://www.littlecaprice-dreams.com'
    ]

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': "//article/div[@class='entry-content']//div[contains(@class,'et_section_regular')]//div[contains(@class,'et_pb_row_1-4_3-4')]//div[contains(@class,'et_pb_column_3_4')]//div[contains(@class,'et_pb_text')]/text()",
        'performers': '//div[contains(@class, "et_pb_text_align_left")]/ul/li[contains(., "Models")]/a/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '',
        'external_id': 'project/([a-z0-9-_]+)/?',
        'trailer': '',
        'pagination': '/videos/?page=%s'
    }

    def start_requests2(self, response):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta={'page': self.page, 'pagination': pagination, "playwright": True}, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.css('.et_pb_portfolio_items .et_pb_portfolio_item a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath('//style[contains(text(), ".vid_bg")]/text()').get
            image = image.replace("\n", "").replace("\r", "").replace("\t", "").replace("  ", " ")
            image = re.search(r'vid_bg.*?background:\s+?url\(\'(.*?)\'', image)
            if image:
                image = image.group(1)
        return image
