import re
import requests
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SitePeachyKeenFilmsSpider(BaseSceneScraper):
    name = 'PeachyKeenFilms'
    site = 'Peachy Keen Films'
    parent = 'Peachy Keen Films'
    network = 'Peachy Keen Films'

    start_urls = [
        'https://www.pkfstudios.com',
    ]

    cookies = [{"domain":"www.pkfstudios.com","expirationDate":1771714286,"hostOnly":true,"httpOnly":false,"name":"surbma-yes-no-popup","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"yes"}]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
    }

    selector_map = {
        'title': '//h1[contains(@class, "entry-title")]/text()',
        'description': '//div[@class="wp-video"]/following-sibling::p/text()',
        'date': '//time[@class="entry-date"]/@datetime',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[@class="post-thumbnail"]/img/@data-lazy-src',
        'performers': '',
        'tags': '//span[@class="cat-links"]/a/text()',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/updates/page/%s/',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
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

    async def start(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))        
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = self.copy_meta(response)
        url = self.get_next_page_url(response.url, meta['page'])
        yield scrapy.Request(url, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//header[@class="entry-header"]//h1/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="entry-content"]/p/strong[contains(text(), "Starring")]/text()')
        if performers:
            performers = performers.get()
            performers = performers.lower()
            performers = performers.replace("starring", "").strip()
            if " and " in performers:
                performers = performers.split(" and ")
            else:
                performers = [performers]

            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []

    def get_trailer(self, response):
        trailer = response.xpath('//video/source/@src')
        if trailer:
            trailer = trailer.get()
        if "?" in trailer:
            trailer = re.search(r'(.*?)\?', trailer).group(1)
        if not trailer:
            trailer = ""
        return trailer.replace(" ", "%20")
