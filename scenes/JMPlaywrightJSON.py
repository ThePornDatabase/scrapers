import re
import json
import scrapy
from scrapy.utils.project import get_project_settings
import base64
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class JMPlaywrightJSONSpider(BaseSceneScraper):
    name = 'JMPlaywrightJSON'

    start_url = 'https://www.jacquieetmicheltv.net'

    paginations = [
        '/en/content/list?studio=6352b65e8b4552ba57ee0e7d&page=%s',
        '/en/content/list?studio=63626ce889913bab98631473&page=%s',
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
        'pagination': '/en/content/list?studio=6352b65e8b4552ba57ee0e7d&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        # ~ meta['playwright'] = True
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers={"Accept": "application/json"}, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        # ~ print(response.text)
        jsondata = json.loads(response.text)
        taglist = jsondata['facets']['tags']
        scenelist = jsondata['contents']
        for scene in scenelist:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            # ~ item['description'] = scene['description']
            # ~ item['description'] = re.sub('<[^<]+?>', '', item['description']).replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("  ", " ").strip()
            # ~ item['duration'] = str(int(scene['duration']) * 60)
            if "mixpanel" in scene and scene['mixpanel']:
                mixpanel = json.loads(base64.b64decode(scene['mixpanel']))
                if mixpanel['contentDuration']:
                    item['duration'] = str(mixpanel['contentDuration'])
            item['description'] = ""
            item['date'] = scene['publication_date']['iso']
            item['image'] = scene['poster']['thumbnail']['srcSet']
            item['image'] = re.search(r'^(http.*?)\s', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['type'] = 'Scene'
            item['url'] = self.format_link(response, scene['routes']['details']).replace("www.", "")
            item['id'] = re.search(r'content/(.*?)/', item['url']).group(1)
            if "6352b65e8b4552ba57ee0e7d" in response.url:
                item['site'] = "Jacquie et Michel"
            if "63626ce889913bab98631473" in response.url:
                item['site'] = "Dompteuse"
            item['parent'] = "Jacquie et Michel"
            item['network'] = "Jacquie et Michel"
            item['tags'] = []
            if "tags" in scene:
                for tag in scene['tags']:
                    for tagref in taglist:
                        if tag == tagref['id']:
                            item['tags'].append(tagref['name'])
                            break
            item['performers'] = []
            item['trailer'] = ''

            yield self.check_item(item, self.days)
