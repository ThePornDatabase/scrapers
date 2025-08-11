import re
import string
import scrapy
from PIL import Image
import base64
from io import BytesIO
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from tpdb.helpers.http import Http


class NetworkKinkMenSpider(BaseSceneScraper):
    name = 'KinkMenPlaywright'
    network = "Kink"

    url = 'https://www.kinkmen.com'

    paginations = [
        '/shoots?sort=published&page=%s',
        # ~ '/shoots/featured?page=%s',
        # ~ '/shoots/partner?page=%s',
        # ~ '/shoots?channelIds=takenrough&page=%s',
    ]

    # ~ headers = {
        # ~ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        # ~ "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        # ~ "Accept-Language": "en-US,en;q=0.5",
        # ~ "Accept-Encoding": "gzip, deflate",
        # ~ "Connection": "keep-alive",
        # ~ "Upgrade-Insecure-Requests": "1",
        # ~ "Sec-Fetch-Dest": "document",
        # ~ "Sec-Fetch-Mode": "navigate",
        # ~ "Sec-Fetch-Site": "none",
        # ~ "Sec-Fetch-User": "?1",
        # ~ "Cache-Control": "max-age=0",
    # ~ }

    selector_map = {
        'title': '//h1/text()',
        'description': '//span[contains(text(), "Description")]/following-sibling::span[1]/p/text()',
        'date': '//script[contains(text(), "KinkyTracking.all")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class, "kvjs-container")]/@data-setup',
        're_image': r'thumbnailUrl.*?(http.*?)[\'\"]',
        'performers': '//h1/following-sibling::span[1]/a/text()',
        'tags': '//p[contains(text(), "Categories")]/following-sibling::span[1]/a/text()',
        'director': '//p[contains(text(), "Director")]/following-sibling::p[1]/span/a/text()',
        'duration': '//span[contains(@class, "clock")]/text()',
        'external_id': r'/shoot/(\d+)',
        'trailer': '//div[contains(@class, "kvjs-container")]/@data-setup',
        're_trailer': r'thumbnailUrl.*?[\'\"]url[\'\"].*?(http.*?)[\'\"]',
        'pagination': '/shoots/latest?page=%s'
    }

    # ~ custom_scraper_settings = {
        # ~ 'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        # ~ 'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        # ~ 'AUTOTHROTTLE_START_DELAY': 1,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 60,
        # ~ 'CONCURRENT_REQUESTS': 1,
        # ~ 'DOWNLOAD_DELAY': 2,
        # ~ 'DOWNLOADER_MIDDLEWARES': {
            # ~ # 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            # ~ 'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            # ~ 'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            # ~ 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # ~ 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # ~ 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            # ~ 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        # ~ },
        # ~ 'DOWNLOAD_HANDLERS': {
            # ~ "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            # ~ "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        # ~ }
    # ~ }

    def start_requests(self):
        # ~ yield scrapy.Request("https://www.kinkmen.com", callback=self.start_requests2, headers=self.headers, cookies=self.cookies, meta={"playwright": True})
        yield scrapy.Request("https://www.kinkmen.com", callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta={}
        meta['page'] = self.page
        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta=meta)

    def parse(self, response, **kwargs):
        if response.status == 200:
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
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "shoot-thumbnail")]/div[1]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return response.xpath('//div[@id="shootPage"]/@data-channelname').get().strip()

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        performers_stripped = [s.strip() for s in performers]
        performers_stripped = [s.rstrip(',') for s in performers_stripped]
        return list(map(lambda x: x.strip(), performers_stripped))

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if hasattr(self, 'site'):
            item['site'] = self.site
        elif 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if 'image_blob' in response.meta:
            item['image_blob'] = response.meta['image_blob']
        else:
            item['image_blob'] = self.get_image_blob(response)

        if ('image_blob' not in item or not item['image_blob']) and item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if 'image_blob' not in item:
            item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if item['performers']:
            item['performers_data'] = self.get_performers_data(response, item['site'])

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'markers' in response.meta:
            item['markers'] = response.meta['markers']
        else:
            item['markers'] = self.get_markers(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        if 'duration' in response.meta:
            item['duration'] = response.meta['duration']
        else:
            item['duration'] = self.get_duration(response)

        if 'url' in response.meta:
            item['url'] = response.meta['url']
        else:
            item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        elif 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        elif 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        # Movie Items

        if 'store' in response.meta:
            item['store'] = response.meta['store']
        else:
            item['store'] = self.get_store(response)

        if 'director' in response.meta:
            item['director'] = response.meta['director']
        else:
            item['director'] = self.get_director(response)

        if 'format' in response.meta:
            item['format'] = response.meta['format']
        else:
            item['format'] = self.get_format(response)

        if 'back' in response.meta:
            item['back'] = response.meta['back']
        else:
            item['back'] = self.get_back_image(response)

        if 'back' not in item or not item['back']:
            item['back'] = None
            item['back_blob'] = None
        else:
            if 'back_blob' in response.meta:
                item['back_blob'] = response.meta['back_blob']
            else:
                item['back_blob'] = self.get_image_back_blob(response)

            if ('back_blob' not in item or not item['back_blob']) and item['back']:
                item['back_blob'] = self.get_image_from_link(item['back'])

        if 'back_blob' not in item:
            item['back_blob'] = None

        if 'sku' in response.meta:
            item['sku'] = response.meta['sku']
        else:
            item['sku'] = self.get_sku(response)

        if hasattr(self, 'type'):
            item['type'] = self.type
        elif 'type' in response.meta:
            item['type'] = response.meta['type']
        elif 'type' in self.get_selector_map():
            item['type'] = self.get_selector_map('type')
        else:
            item['type'] = 'Scene'

        matches = ['str8hell', 'cfnmeu', 'malefeet4u', 'williamhiggins', 'ambushmassage', 'swnude', 'sweetfemdom', 'masqulin']
        if not any(x in item['site'] for x in matches):
            yield self.check_item(item, self.days)

    def get_image_blob_from_link(self, image):
        if image:
            data = self.get_image_from_link(image)
            if data:
                try:
                    img = BytesIO(data)
                    img = Image.open(img)
                    img = img.convert('RGB')
                    width, height = img.size
                    if height > 1080 or width > 1920:
                        img.thumbnail((1920, 1080))
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    data = buffer.getvalue()
                except:
                    print(f"Could not decode image for evaluation: '{image}'")
                return base64.b64encode(data).decode('utf-8')
        return None

    def get_performers_data(self, response, site):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "Kink"
            performer_extra['site'] = site
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
