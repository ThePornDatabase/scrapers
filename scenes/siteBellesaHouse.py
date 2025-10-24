import re
import string
import json
import scrapy
from datetime import datetime
from tpdb.BaseSceneScraper import BaseSceneScraper
from slugify import slugify
from tpdb.helpers.http import Http
import requests
true = True
false = False


class SiteBellesaHouseSpider(BaseSceneScraper):
    name = 'BellesaHouse'
    network = 'Bellesa'

    start_urls = [
        'https://www.bellesa.co',
        'https://bellesaplus.co',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
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
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    def get_next_page_url(self, base, page):
        if "bellesa.co" in base:
            pagination = "/api/rest/v1/videos?filter%5Bprovider%5D=or%3Abellesa-films%2Cbellesa-house%2Cbellesa-blind-date%2Czero-to-hero%2Cbelle-says%2Cbellesa-house-party&filter%5Bsource%5D=bellesa&limit=24&page=<PAGE>"
        if "bellesaplus.co" in base:
            pagination = "/api/rest/v1/videos?filter%5Bprovider%5D=or%3Abellesa-films%2Cbellesa-house%2Cbellesa-blind-date%2Czero-to-hero%2Cbelle-says%2Cbellesa-house-party&limit=24&page=<PAGE>&sources=plus"
        link = self.format_url(base, pagination.replace("<PAGE>", str(page)))
        return link

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            url=self.get_next_page_url(link, self.page)
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def get_scenes(self, response):
        if "<pre>" in response.text.lower():
            raw_json = response.css("pre::text").get()
        else:
            raw_json = response.text
        jsondata = json.loads(raw_json)
        for scene in jsondata:
            item = self.init_scene()

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
            if self.check_item(item, self.days):
                item['id'] = scene['id']
                item['performers'] = []
                for performer in scene['performers']:
                    item['performers'].append(performer['name'])
                item['tags'] = scene['tags'].split(",")
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))
                item['tags'] = self.clean_tags(item['tags'], item['performers'])
                item['tags'].append("Unscripted")
                item['tags'].append("Ethical Porn")
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

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.status_code == 200:
                return req.content
        return None
