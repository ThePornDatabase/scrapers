import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ATKGirlfriendsPlaywrightSpider(BaseSceneScraper):
    name = 'ATKGirlfriendsPlaywright'
    network = 'ATK Girlfriends'
    parent = 'ATK Girlfriends'

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    start_urls = [
        'https://www.atkgirlfriends.com',
    ]

    headers = {
        'referer': 'https://www.atkgirlfriends.com',
    }

    selector_map = {
        'title': '//title/text()',
        'description': '//b[contains(text(),"Description")]/following-sibling::text()[1]',
        'date': '',
        'image': '//div[contains(@style,"background")]/@style',
        'image_blob': True,
        're_image': r'url\(\'(http.*)\'\)',
        'performers': '//div[contains(@class,"model-profile-wrap")]/text()[1]',
        'tags': '//b[contains(text(),"Tags")]/following-sibling::text()',
        'external_id': r'/tour/.+?/(.*)?/',
        'trailer': '',
        'pagination': '/tour/movies/%s'
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

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request("https://www.atkgirlfriends.com/", callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"movie-wrap")]')
        for scene in scenes:
            link = scene.xpath('.//div[@class="movie-image"]/a/@href').get()
            link = "https://www.atkgirlfriends.com" + link
            scenedate = scene.xpath('.//div[contains(@class,"left")]/text()').get()
            if scenedate:
                meta['date'] = self.parse_date(scenedate.strip()).isoformat()
            else:
                meta['date'] = None
            duration = scene.xpath('.//div[@class="movie-duration"]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())
            else:
                meta['duration'] = None
            if "join.atkgirlfriends.com" not in link:
                item = SceneItem()
                title = scene.xpath('./div/a/text()').getall()
                title = " ".join(title)
                title = title.strip()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''
                image = scene.xpath('.//img/@alt').get()
                if "compilation" in image.lower():
                    item['title'] = "Compilation: " + item['title']

                item['date'] = meta['date']
                item['duration'] = meta['duration']

                image = scene.xpath('./div/a/img/@src').get()
                if image:
                    item['image'] = image.strip().replace("/sm_", "/")
                else:
                    item['image'] = None

                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['image'] = re.search(r'(.*\.\w{3,4})', item['image']).group(1)

                url = scene.xpath('./div/a[contains(@href,"/model/")]/@href').get()
                if url:
                    item['url'] = "https://www.atkgirlfriends.com" + url.strip()
                else:
                    item['url'] = ''
                sceneid = re.search(r'.*/(\d+)/', item['image'])
                if sceneid:
                    item['id'] = sceneid.group(1)
                item['performers'] = []
                item['tags'] = []
                item['trailer'] = ''
                item['description'] = ''
                item['site'] = "ATK Girlfriends"
                item['parent'] = "ATK Girlfriends"
                item['network'] = "ATK Girlfriends"

                if item['title'] and item['image']:
                    meta['item'] = item.copy()
                    yield scrapy.Request(link, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)
            else:
                item = SceneItem()
                title = scene.xpath('./div/a/text()').getall()
                title = " ".join(title)
                title = title.strip()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''
                image = scene.xpath('.//img/@alt').get()
                if "compilation" in image.lower():
                    item['title'] = "Compilation: " + item['title']

                item['date'] = meta['date']
                item['duration'] = meta['duration']

                image = scene.xpath('./div/a/img/@src').get()
                if image:
                    item['image'] = image.strip().replace("/sm_", "/")
                else:
                    item['image'] = None

                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['image'] = re.search(r'(.*\.\w{3,4})', item['image']).group(1)

                url = scene.xpath('./div/a[contains(@href,"/model/")]/@href').get()
                if url:
                    item['url'] = "https://www.atkgirlfriends.com" + url.strip()
                else:
                    item['url'] = ''
                sceneid = re.search(r'.*/(\d+)/', item['image'])
                if sceneid:
                    item['id'] = sceneid.group(1)
                item['performers'] = []
                item['tags'] = []
                item['trailer'] = ''
                item['description'] = ''
                item['site'] = "ATK Girlfriends"
                item['parent'] = "ATK Girlfriends"
                item['network'] = "ATK Girlfriends"

                if item['title'] and item['image']:
                    yield self.check_item(item, self.days)

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).get()
            if tags:
                tags = tags.split(",")

                tags2 = tags.copy()
                for tag in tags2:
                    matches = ['4k']
                    if any(x in tag.lower() for x in matches):
                        tags.remove(tag)

                return list(map(lambda x: x.strip().title(), tags))
        return []

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()

        item['title'] = self.get_title(response)
        if item['title']:
            item['date'] = meta['date']
            item['duration'] = meta['duration']
            item['description'] = self.get_description(response)
            item['image'] = self.get_image(response)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(response)
            item['tags'] = self.get_tags(response)
            item['id'] = re.search(r'/movie/(\d+)/', response.url).group(1)
            item['trailer'] = self.get_trailer(response)
            item['url'] = response.url
            item['network'] = "ATK Girlfriends"
            item['parent'] = "ATK Girlfriends"
            item['site'] = "ATK Girlfriends"
        else:
            item = meta['item']
        yield self.check_item(item, self.days)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "/" not in image:
            image = response.xpath('//div[contains(@style,"background")]/@style')
            if image:
                image = image.get()
        if "url(" in image:
            image = re.search(r'url\([\"\'](http.*)(?:[\"\']\))?$', image)
            if image:
                image = image.group(1)

        if image:
            image = self.format_link(response, image)
        return image.replace(" ", "%20")
