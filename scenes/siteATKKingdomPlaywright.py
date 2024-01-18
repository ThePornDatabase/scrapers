import re
import scrapy
from slugify import slugify
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

        network = "ATK Girlfriends"
        if "atkarchives" in response.url:
            parent = "ATK Archives"
            site = "ATK Archives"
        if "atkexotics" in response.url:
            parent = "ATK Exotics"
            site = "ATK Exotics"
        if "atkpremium" in response.url:
            parent = "ATK Premium"
            site = "ATK Premium"
        if "atkpetites" in response.url:
            parent = "ATK Petites"
            site = "ATK Petites"
        if "atkhairy" in response.url:
            parent = "ATK Hairy"
            site = "ATK Hairy"
        if "amkingdom" in response.url:
            parent = "ATK Galleria"
            site = "ATK Galleria"

        for scene in scenes:
            if "atkexotics" in response.url or "amkingdom" in response.url:
                link = scene.xpath('./div[@class="movie-image"]/a/@href').get()
                scenedate = scene.xpath('./div[@class="date left clear"][2]/text()').get()
                if scenedate:
                    scenedate = self.parse_date(scenedate.strip()).strftime('%Y-%m-%d')
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

                origtitle = scene.xpath('./div[@class="video-name"]/a/text()')
                if origtitle:
                    origtitle = self.cleanup_title(origtitle.get())

                origimage = scene.xpath('.//img/@src')
                if origimage:
                    origimage = self.format_link(response, origimage.get())
                    origimage_blob = self.get_image_blob_from_link(origimage)

            else:
                link = scene.xpath('.//div[@class="player"]/a/@href').get()
                scenedate = scene.xpath('.//span[contains(@class, "movie_date")]/text()').get()
                if scenedate:
                    scenedate = self.parse_date(scenedate.strip()).strftime('%Y-%m-%d')
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

                origtitle = scene.xpath('./div/span/a/text()')
                if origtitle:
                    origtitle = self.cleanup_title(origtitle.get())

                origimage = scene.xpath('.//img/@src')
                if origimage:
                    origimage = self.format_link(response, origimage.get())
                    origimage_blob = self.get_image_blob_from_link(origimage)

            sceneid = re.search(r'.*/(\d{4,8})/.*', link)
            if sceneid:
                sceneid = sceneid.group(1)
            else:
                sceneid = re.search(r'.*/(\d{4,8})/.*', origimage)
                if sceneid:
                    sceneid = sceneid.group(1)

            urltitle = origtitle
            origtitle = f"{site} : {origtitle} - {sceneid}"

            linktitle = ''
            if re.search(r'(movie/\d+/)', link) and "?w=" not in link and ".com?nats" not in link:
                linktitle = re.search(r'.*/\d+/(.*?)$', link)
                if linktitle:
                    linktitle = linktitle.group(1)
                    linktitle = linktitle.strip("/")

            if len(linktitle) > len(urltitle):
                origtitle = self.cleanup_title(linktitle.replace("-", " "))

            meta['origtitle'] = origtitle
            meta['origimage'] = origimage
            meta['origimage_blob'] = origimage_blob

            meta['date'] = scenedate
            meta['performers'] = [performer]

            if "?w=" not in link and ".com?nats" not in link:
                yield scrapy.Request(self.format_link(response, link), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
            else:
                item = SceneItem()
                item['network'] = network
                item['site'] = site
                item['parent'] = parent

                if origtitle:
                    item['title'] = origtitle
                else:
                    item['title'] = ''
                item['date'] = scenedate
                item['url'] = self.format_link(response, f"/tour/movies/{sceneid}/" + slugify(re.sub('[^a-z0-9- ]', '', urltitle.lower().strip())))
                if origimage:
                    item['image'] = origimage
                    item['image_blob'] = origimage_blob
                else:
                    item['image'] = ''
                    item['image_blob'] = ''

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

                if item['title']:
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
        # ~ print(meta)
        item = SceneItem()
        item['date'] = meta['date']
        item['performers'] = meta['performers']
        item['duration'] = meta['duration']

        item['title'] = self.get_title(response)
        if not item['title']:
            item['title'] = meta['origtitle']
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = meta['origimage']
            item['image_blob'] = meta['origimage_blob']
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

        if item['title']:
            yield self.check_item(item, self.days)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or ".com/" not in image:
            imagealt = response.xpath('//div[contains(@style,"background")]/@style')
            if not imagealt:
                imagealt = response.xpath('//div[@id="movie-poster"]/video/@poster')
            if imagealt:
                imagealt = imagealt.get()
                imagealt = re.search(r'url\(\"(http.*)\"\)', imagealt)
                if imagealt:
                    imagealt = imagealt.group(1)
                    imagealt = self.format_link(response, imagealt)
                    return imagealt.replace(" ", "%20")
        if not image or ".com/" not in image:
            imagealt = response.xpath('//video/@poster')
            if imagealt:
                imagealt = imagealt.get()
                return imagealt.replace(" ", "%20")
        else:
            return image
        return None
