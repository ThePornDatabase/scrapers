import re
from requests import get
import scrapy
import string

from scrapy_playwright.page import PageMethod
from tpdb.BaseSceneScraper import BaseSceneScraper


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

    async def start(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        meta['playwright_page_methods'] = [
            PageMethod('wait_for_selector', 'div[class*="movie-wrap"]'),
        ]
        
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"movie-wrap")]')
        for scene in scenes:
            link = scene.xpath('.//div[@class="movie-image"]/a/@href').get()
            link = "https://www.atkgirlfriends.com" + link
            scenedate = scene.xpath('./div[@class="vid-count left"]/text()').get()
            if scenedate:
                meta['scenedate'] = self.parse_date(scenedate.strip()).strftime('%Y-%m-%d')

            if "join.atkgirlfriends.com" not in link:
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta)
            else:
                item = self.init_scene()
                title = scene.xpath('./div/a/text()').get()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''
                if meta['scenedate']:
                    item['date'] = meta['scenedate']

                image = scene.xpath('./div/a/img/@src')
                if image:
                    image = image.get()
                    if "url('http" in image:
                        image = re.search(r'url\(\'(http.*)', image)
                        if image:
                            image = image.group(1)  
                    item['image'] = image.strip().replace("/sm_", "/")
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                if item['image']:
                    sceneid = re.search(r'.*/\w{2,4}\d{2,4}/(\d+)/', item['image'])
                    if sceneid:
                        item['id'] = sceneid.group(1)

                url = scene.xpath('./div/a[contains(@href,"/model/")]/@href').get()
                if url:
                    item['url'] = "https://www.atkgirlfriends.com" + url.strip()

                if not item['id']:
                    externalid = item['title'].replace(" ", "-").lower()
                    externalid = re.sub('[^a-zA-Z0-9-]', '', externalid)
                    item['id'] = externalid
                # ~ item['id'] = re.search(r'/model/(.*?)/', jsondata['solution']['url']).group(1)

                item['performers'] = []
                item['tags'] = []
                item['trailer'] = ''
                item['description'] = ''
                item['site'] = "ATK Girlfriends"
                item['parent'] = "ATK Girlfriends"
                item['network'] = "ATK Girlfriends"

                if item['title'] and item['image']:
                    if "url" in item and item['url'] and "com001" not in item['url'] and "compilation" not in item['url'].lower():
                        meta['item'] = item.copy()
                        yield scrapy.Request(item['url'], callback=self.parse_join_scene, meta=meta)
                    else:
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
        item = self.init_scene()
        if "scenedate" in meta and meta['scenedate']:
            item['date'] = self.parse_date(meta['scenedate']).strftime('%Y-%m-%d')

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        if item['image']:
            item['image'] = item['image']
            if "url('http" in item['image']:
                item['image'] = re.search(r'url\(\'(http.*)', item['image'])
                if item['image']:
                    item['image'] = item['image'].group(1)  
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['performers'] = []
        item['performers_data'] = []
        performers = response.xpath('//div[contains(@class,"model-profile-wrap")]')
        perfArray = []
        for perf in performers:
            temp_perf = {}
            temp_perf['name'] = perf.xpath('./text()[1]').get()
            temp_perf['image'] = perf.xpath('.//img/@src').get()
            if temp_perf['name']:
                temp_perf['name'] = string.capwords(temp_perf['name'].strip())
                temp_perf_url = perf.xpath('./a[1]/@href').get()
                temp_perf['id'] = re.search(r'.*/(\w{2,4}\d{2,4})/.*?$', temp_perf_url).group(1)
                performer = temp_perf['name']
                if " " not in performer:
                    performer = performer + " " + temp_perf['id']
                item['performers'].append(performer)
                perf = {}
                perf['name'] = performer
                perf['image'] = temp_perf['image']
                perf['extra'] = {'gender': "Female"}
                perf['site'] = "ATK Girlfriends"
                perf['url'] = f"https://www.atkgirlfriends.com{temp_perf_url}"
                item['performers_data'].append(perf)
                # perfArray.append(temp_perf)

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
        if not image or image in response.url:
            imagealt = response.xpath('//div[contains(@style,"background")]/@style')
            if imagealt:
                imagealt = re.search(r'url\(\"(http.*)\"\)', imagealt.get())
                if imagealt:
                    imagealt = imagealt.group(1)
                    imagealt = self.format_link(response, imagealt)
                    return imagealt.replace(" ", "%20")
        return image

    def parse_join_scene(self, response):
        meta = response.meta
        item = meta['item']
        item['performers'] = []
        item['performers_data'] = []
        performers = response.xpath('//div[contains(@class,"model-profile-wrap")]')
        perfArray = []
        for perf in performers:
            temp_perf = {}
            temp_perf['name'] = perf.xpath('//h1[contains(@class, "page-title")]/text()').get()
            temp_perf['image'] = perf.xpath('.//img/@src').get()
            if temp_perf['name']:
                temp_perf['name'] = string.capwords(temp_perf['name'].strip())
                temp_perf_url = response.url
                temp_perf['id'] = re.search(r'.*model/(\w{2,4}\d{2,4})/', temp_perf_url).group(1)
                performer = temp_perf['name']
                if " " not in performer:
                    performer = performer + " " + temp_perf['id']
                item['performers'].append(performer)
                perf = {}
                perf['name'] = performer
                perf['image'] = temp_perf['image']
                perf['extra'] = {'gender': "Female"}
                perf['site'] = "ATK Girlfriends"
                perf['url'] = response.url
                item['performers_data'].append(perf)
                # perfArray.append(temp_perf)

        desc_xpath = (
            f'//h1[contains(@class, "video-title") and '
            f'contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), '
            f'"{item["title"].lower()}")]'
            f'/ancestor::div[contains(@class,"movie-wrap-index")]'
            f'//b[contains(text(), "Description:")]/following-sibling::text()'
        )

        description = response.xpath(desc_xpath)

        if description:
            description = " ".join(description.getall()).strip()
            item['description'] = description

        yield self.check_item(item, self.days)