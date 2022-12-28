import re
import json
import scrapy
from scrapy.utils.project import get_project_settings

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class JMElitePlaywrightJSONSpider(BaseSceneScraper):
    name = 'JMElitePlaywrightJSON'

    start_urls = [
        'https://www.jacquieetmicheltv.net',
    ]

    # ~ cookies = {
    # ~ 'dscl': '1',
    # ~ 'my18passwidget-open': '0',
    # ~ 'ppndr': '1',
    # ~ 'force-my18pass-refresh	': '0',
    # ~ }

    headers = {"accept": "application/json"}

    # ~ custom_scraper_settings = {
    # ~ 'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    # ~ 'AUTOTHROTTLE_ENABLED': True,
    # 'USE_PROXY': True,
    # ~ 'AUTOTHROTTLE_START_DELAY': 1,
    # ~ 'AUTOTHROTTLE_MAX_DELAY': 60,
    # ~ 'CONCURRENT_REQUESTS': 1,
    # ~ 'DOWNLOAD_DELAY': 2,
    # ~ 'DOWNLOADER_MIDDLEWARES': {
    # ~ 'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
    # ~ 'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
    # ~ 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # ~ 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    # ~ 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    # ~ 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    # ~ 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 100,
    # ~ },
    # ~ 'DOWNLOAD_HANDLERS': {
    # ~ "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    # ~ "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    # ~ }
    # ~ }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/en/content/list?studio=6352b85b8b4552ba57ee7cb0&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        settings = get_project_settings()

        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        meta = {}
        # ~ meta['playwright'] = True
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
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers={"Accept": "application/json"}, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        taglist = jsondata['facets']['tags']
        scenelist = jsondata['contents']['data']
        for scene in scenelist:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['description'] = scene['description']
            item['description'] = re.sub('<[^<]+?>', '', item['description']).replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("  ", " ").strip()
            item['duration'] = str(int(scene['duration']) * 60)
            item['date'] = scene['publication_date']['iso']
            item['image'] = scene['poster']['thumbnail']['srcSet']
            item['image'] = re.search(r'^(http.*?)\s', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['type'] = 'Scene'
            item['id'] = scene['id']
            item['url'] = self.format_link(response, scene['routes']['content']).replace("www.", "")
            item['site'] = "Jacquie et Michel Elite"
            item['parent'] = "Jacquie et Michel Elite"
            item['network'] = "Jacquie et Michel"
            item['tags'] = []
            for tag in scene['tags']:
                for tagref in taglist:
                    if tag == tagref['id']:
                        item['tags'].append(tagref['name'])
                        break
            item['performers'] = []
            item['trailer'] = ''

            yield self.check_item(item, self.days)
