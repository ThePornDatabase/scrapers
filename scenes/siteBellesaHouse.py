import re
import string
import json
import scrapy
from datetime import datetime
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from slugify import slugify


class SiteBellesaHouseSpider(BaseSceneScraper):
    name = 'BellesaHouse'
    network = 'Bellesa'

    start_urls = [
        'https://www.bellesa.co',
        'https://www.bellesaplus.co',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?page=<PAGE>&providers=bellesa-films%2Cbellesa-house%2Cbellesa-blind-date%2Czero-to-hero%2Cbelle-says%2Cbellesa-house-party',
        'type': 'Scene',
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
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True

        link = "https://bellesaplus.co/studio-preview/bellesa-originals/"
        yield scrapy.Request(link, callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination').replace("<PAGE>", str(page)))

    def get_scenes(self, response):
        jsondata = response.xpath('//script[@id="data-script"]/text()').get()
        jsondata = re.search(r'(\{.*\})', jsondata).group(1)
        jsondata = json.loads(jsondata)
        for scene in jsondata['videos']:
            item = SceneItem()

            if scene['title']:
                item['title'] = self.cleanup_title(scene['title'].replace("&", "and"))
            else:
                item['title'] = None

            if scene['description']:
                item['description'] = self.cleanup_description(scene['description'])
            else:
                item['description'] = ''
            item['duration'] = scene['duration']
            datetime_obj = datetime.fromtimestamp(scene['posted_on'])
            item['date'] = datetime_obj.strftime('%Y-%m-%d')
            item['id'] = scene['id']
            item['performers'] = []
            for performer in scene['performers']:
                item['performers'].append(performer['name'])
            item['tags'] = scene['tags'].split(",")
            item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))
            item['tags'] = self.clean_tags(item['tags'], item['performers'])
            item['image'] = self.format_link(response, scene['image'])
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = None
            item['site'] = 'Bellessa House'
            item['parent'] = 'Bellessa House'
            item['network'] = 'Bellessa'
            if scene['content_provider']:
                if 'name' in scene['content_provider'][0] and scene['content_provider'][0]['name']:
                    item['site'] = scene['content_provider'][0]['name']
                    item['parent'] = scene['content_provider'][0]['name']

            slug = slugify(re.sub('[^a-z0-9- ]', '', item['title'].lower().strip()))
            item['url'] = f"https://www.bellesa.co/videos/{item['id']}/{slug}"
            yield self.check_item(item, self.days)

    def clean_tags(self, tags, performers):
        tags2 = []
        for tag in tags:
            if "bellesa" not in tag.lower():
                if "original" not in tag.lower():
                    if tag not in performers:
                        if "." in tag:
                            tags = tag.split(".")
                            for tag in tags:
                                tags2.append(string.capwords(tag.strip()))
                        else:
                            tags2.append(tag)
        return tags2
