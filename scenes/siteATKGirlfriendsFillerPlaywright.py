import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ATKGirlfriendsPlaywrightSpider(BaseSceneScraper):
    name = 'ATKGirlfriendsFillerPlaywright'
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
        're_image': r'(http.*)[\'\"]',
        'performers': '//div[contains(@class,"model-profile-wrap")]/text()[1]',
        'tags': '//b[contains(text(),"Tags")]/following-sibling::text()',
        'external_id': r'/tour/.+?/(.*)?/',
        'trailer': '',
        'pagination': '/tour/lmodels?page=%s'
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

    def parse(self, response, **kwargs):
        scenes = self.get_models(response)
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

    def get_models(self, response):
        meta = response.meta
        models = response.xpath('//div[contains(@class,"model-profile-wrap")]/a/@href').getall()
        for model in models:
            link = self.format_link(response, model)
            yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"movie-wrap-index")]')
        for scene in scenes:
            link = scene.xpath('.//a/@href').get()
            link = "https://www.atkgirlfriends.com" + link
            duration = scene.xpath('.//div[@class="movie-duration"]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}:)?\d{1,2}:\d{2})', duration)
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))
            else:
                meta['duration'] = None
            image = scene.xpath('.//img/@src').get()
            if image:
                meta['image'] = image.strip().replace("/sm_", "/")
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            else:
                meta['image'] = None
                meta['image_blob'] = None
            meta['performers'] = [response.xpath('//h1[contains(@class,"page-title")]/text()').get()]

            title = scene.xpath('./div/h1/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())
            if "join.atkgirlfriends.com" not in link:
                yield scrapy.Request(link, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)
            else:
                item = SceneItem()
                title = scene.xpath('./div/h1/text()').get()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''

                item['date'] = None
                item['duration'] = meta['duration']

                item['image'] = meta['image']
                item['image_blob'] = meta['image_blob']
                print(f"Up Top: {meta}")

                item['url'] = response.url

                externalid = item['title'].replace(" ", "-").lower()
                externalid = re.sub('[^a-zA-Z0-9-]', '', externalid)
                item['id'] = externalid

                item['performers'] = meta['performers']
                item['tags'] = []
                item['trailer'] = ''
                item['description'] = scene.xpath('.//b[contains(text(), "escription:")]/following-sibling::text()[1]').get()
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
        if not item['title']:
            if "title" in meta:
                item['title'] = meta['title']
        item['date'] = None
        if "duration" in meta:
            item['duration'] = meta['duration']
        else:
            item['duration'] = None
        item['description'] = self.get_description(response)
        if meta['image']:
            item['image'] = meta['image']
            item['image_blob'] = meta['image_blob']
        else:
            item['image'] = self.get_image(response)
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None
        if ".com/" not in item['image']:
            print(f"Down Below: {meta}")
        item['performers'] = self.get_performers(response)
        if not item['performers']:
            item['performers'] = meta['performers']
        item['tags'] = self.get_tags(response)
        item['id'] = re.search(r'/movie/(.*?)/', response.url).group(1)
        item['trailer'] = self.get_trailer(response)
        item['url'] = response.url
        item['network'] = "ATK Girlfriends"
        item['parent'] = "ATK Girlfriends"
        item['site'] = "ATK Girlfriends"
        yield self.check_item(item, self.days)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "/" not in image:
            imagealt = response.xpath('//div[contains(@style,"background")]/@style')
            if imagealt:
                imagealt = re.search(r'(http.*)[\'\"]', imagealt.get())
                if imagealt:
                    imagealt = imagealt.group(1)
                    imagealt = self.format_link(response, imagealt)
                    return imagealt.replace(" ", "%20")
        return image
