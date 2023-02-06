import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ATKKingdomPlaywrightSpider(BaseSceneScraper):
    name = 'ATKKingdomPlaywright'

    start_urls = [
        'https://www.atkexotics.com',
        'https://www.atkarchives.com',
        'https://www.atkpetites.com',
        'https://www.amkingdom.com',
        'https://www.atkhairy.com',
        'https://www.atkpremium.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//b[contains(text(), "Description:")]/following-sibling::text()[1]|//span[@class="description"]/following-sibling::text()|//span[@class="description"]/following-sibling::span/text()',
        'date': '',
        'image': '//div[contains(@style, "background-image")]/@style',
        're_image': r'(https.*)[\'\"]',
        'performers': '',
        'tags': '//b[contains(text(), "Tags:")]/following-sibling::text()[1]|//span[@class="tags"]/following-sibling::text()',
        'external_id': r'model/(.*?)/',
        'trailer': '',
        'pagination': '/tour/movies/%s'
    }

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

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.start_requests2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        url = self.get_next_page_url(response.url, meta['page'])
        yield scrapy.Request(url, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = {}
        if "atkexotics" in response.url or "amkingdom" in response.url:
            scenes = response.xpath('//div[contains(@class, "movie-wrap")]')
        else:
            scenes = response.xpath('//div[contains(@class, "tourMovieContainer")]')

        for scene in scenes:
            if "atkexotics" in response.url or "amkingdom" in response.url:
                link = scene.xpath('./div[@class="movie-image"]/a/@href').get()
                scenedate = scene.xpath('./div[@class="date left clear"][2]/text()').get()
                if scenedate:
                    scenedate = self.parse_date(scenedate.strip()).isoformat()
                else:
                    scenedate = None
                performer = scene.xpath('./div[@class="video-name"]/a/text()').get()
                performer = performer.strip()
                if not performer:
                    performer = ''
                duration = scene.xpath('.//div[@class="movie-duration"]/text()')
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.get())
                else:
                    meta['duration'] = None

            else:
                link = scene.xpath('.//div[@class="player"]/a/@href').get()
                scenedate = scene.xpath('.//span[contains(@class, "movie_date")]/text()').get()
                if scenedate:
                    scenedate = self.parse_date(scenedate.strip()).isoformat()
                else:
                    scenedate = None
                performer = scene.xpath('./div/span[contains(@class,"video_name")]/a/text()').get()
                performer = performer.strip()
                if not performer:
                    performer = ''
                duration = scene.xpath('.//span[contains(@class, "video_duration")]/text()')
                if duration:
                    duration = re.search(r'(\d{1,2}:\d{2})', duration.get())
                    if duration:
                        meta['duration'] = self.duration_to_seconds(duration.group(1))
                else:
                    meta['duration'] = None

            meta['date'] = scenedate
            meta['performers'] = [performer]

            if "?w=" not in link and ".com?nats" not in link:
                yield scrapy.Request(self.format_link(response, link), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
            else:
                item = SceneItem()
                item['network'] = "ATK Girlfriends"
                if "atkarchives" in response.url:
                    item['parent'] = "ATK Archives"
                    item['site'] = "ATK Archives"
                if "atkexotics" in response.url:
                    item['parent'] = "ATK Exotics"
                    item['site'] = "ATK Exotics"
                if "atkpremium" in response.url:
                    item['parent'] = "ATK Premium"
                    item['site'] = "ATK Premium"
                if "atkpetites" in response.url:
                    item['parent'] = "ATK Petites"
                    item['site'] = "ATK Petites"
                if "atkhairy" in response.url:
                    item['parent'] = "ATK Hairy"
                    item['site'] = "ATK Hairy"
                if "amkingdom" in response.url:
                    item['parent'] = "ATK Galleria"
                    item['site'] = "ATK Galleria"
                title = scene.xpath('.//img/@alt')
                if title:
                    item['title'] = self.cleanup_title(title.get())
                else:
                    item['title'] = ''
                item['date'] = scenedate
                item['url'] = response.url
                image = scene.xpath('.//img/@src')
                if image:
                    item['image'] = image.get().strip()
                else:
                    item['image'] = ''
                if item['image']:
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                performer = scene.xpath('./div[@class="video-name"]/a/text()')
                if performer:
                    item['performers'] = [performer.get().strip()]
                else:
                    item['performers'] = []
                item['description'] = ""
                item['duration'] = meta['duration']
                item['trailer'] = ""
                item['tags'] = []
                if item['image']:
                    item['id'] = re.search(r'.*/(\d{4,8})/.*', item['image']).group(1)

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
        item['date'] = meta['date']
        item['performers'] = meta['performers']
        item['duration'] = meta['duration']

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['tags'] = self.get_tags(response)
        if "" in item['tags']:
            item['tags'].remove("")
        item['id'] = re.search(r'/movie/(.*?)/', response.url).group(1)
        item['trailer'] = self.get_trailer(response)
        item['url'] = response.url
        item['network'] = "ATK Girlfriends"

        if "atkarchives" in response.url:
            item['parent'] = "ATK Archives"
            item['site'] = "ATK Archives"
        if "atkexotics" in response.url:
            item['parent'] = "ATK Exotics"
            item['site'] = "ATK Exotics"
        if "atkpremium" in response.url:
            item['parent'] = "ATK Premium"
            item['site'] = "ATK Premium"
        if "atkpetites" in response.url:
            item['parent'] = "ATK Petites"
            item['site'] = "ATK Petites"
        if "atkhairy" in response.url:
            item['parent'] = "ATK Hairy"
            item['site'] = "ATK Hairy"
        if "amkingdom" in response.url:
            item['parent'] = "ATK Galleria"
            item['site'] = "ATK Galleria"

        yield self.check_item(item, self.days)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or ".com/" not in image:
            imagealt = response.xpath('//div[contains(@style,"background")]/@style')
            if imagealt:
                imagealt = re.search(r'url\(\"(http.*)\"\)', imagealt.get())
                if imagealt:
                    imagealt = imagealt.group(1)
                    imagealt = self.format_link(response, imagealt)
                    return imagealt.replace(" ", "%20")
            image = None
        return image
