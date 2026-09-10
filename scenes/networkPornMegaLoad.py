import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        '18eighteen': "18Eighteen",
        '40somethingmag': "40Somethingmag",
        '50plusmilfs': "50Plus MILFs",
        '60plusmilfs': "60Plus MILFs",
        'bigtithooker': "Big Tit Hooker",
        'bootyliciousmag': "Bootyliciousmag",
        'legsex': "Leg Sex",
        'mickybells': "Micky Bells",
        'naughtymag': "Naughtymag",
        'pornmegaload': "PornMegaLoad",
        'scoreland': "Scoreland",
        'scoreland2': "Scoreland2",
        'scorevideos': "Score Videos",
        'xlgirls': "XL Girls",
    }
    return match.get(argument, argument)


class NetworkPornMegaLoadPlaywrightSpider(BaseSceneScraper):
    name = 'PornMegaLoadPlaywright'
    network = 'ScorePass'

    start_urls = [
        'https://www.pornmegaload.com',
        # -----------------------------------
        # 'https://www.18eighteen.com',
        # 'https://www.40somethingmag.com',
        # 'https://www.50plusmilfs.com',
        # 'https://www.60plusmilfs.com',
        # 'https://www.bigtithooker.com',
        # 'https://www.bootyliciousmag.com',
        # 'https://www.legsex.com',
        # 'https://www.mickybells.com',
        # 'https://www.naughtymag.com',
        # 'https://www.pornmegaload.com',
        # 'https://www.scoreland.com',
        # 'https://www.scorevideos.com',
        # 'https://www.xlgirls.com'
    ]

    custom_scraper_settings = {
        # The Score network refuses this exit outright: TLS completes, the
        # request goes out, then the server kills the stream. It is not a TLS
        # fingerprint (Playwright fails identically) nor a challenge page
        # (FlareSolverr reports "Challenge not detected") -- it is the source
        # address. FlareSolverr runs on a different host and reaches the site
        # normally, so requests are routed through it.
        'DOWNLOAD_TIMEOUT': 180,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        # ~ 'AUTOTHROTTLE_ENABLED': True,
        # ~ 'AUTOTHROTTLE_START_DELAY': 1,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        # 'DOWNLOAD_DELAY': 60,
        # 'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'SPIDERMON_ENABLED': False,
        'DOWNLOAD_FAIL_ON_DATALOSS': True,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 408, 307, 403],
        'HANDLE_HTTPSTATUS_LIST': [500, 503, 504, 400, 408, 307, 403],
        # The Playwright handlers were dropped: a real browser cannot reach this
        # network from here either, so rendering bought nothing and only hid the
        # block. FlareSolverr does the fetching now.
    }

    selector_map = {
        'title': '//main/div/section/div[@class="row"]/div/h1/text()|//section[@id="videos_page-page"]/div[contains(@class,"ali-center")]//h2/text()|//div[@itemprop="articleBody"]/h2/text()',
        'description': '//div[contains(@class, "p-desc")]//text()',
        'date': '//div[contains(@class, "stat")]/span[contains(text(), "Date")]/following-sibling::span/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content|//video/@poster',
        'performers': '//div[contains(@class, "stat")]/span[contains(text(), "Featuring")]/following-sibling::span/a/text()',
        'tags': '//a[contains(@href, "updates-tag")]/text()',
        'duration': '//div[contains(@class, "stat")]/span[contains(text(), "Duration")]/following-sibling::span/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': r'.*/(\d+)/',
        'trailer': '//div[contains(@class, "mr-lg")]//video/source[1]/@src',
        'pagination': '/hd-porn-scenes/?page=%s'
    }

    def get_date(self, response):
        # Dates read "September 8th, 2026"; the ordinal has to go before
        # %B %d, %Y will match. (The map key was also 'date_format', which the
        # base class never reads -- it looks for 'date_formats'.)
        scenedate = self.process_xpath(response, self.get_selector_map('date')).get()
        if scenedate:
            scenedate = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', scenedate.strip())
            parsed = self.parse_date(scenedate, date_formats=self.get_selector_map('date_formats'))
            if parsed:
                return parsed.isoformat()
        return ''

    async def start(self):
        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # Card class is now "li-item compact h-100 video".
        scenes = response.xpath(
            '//div[contains(@class, "li-item") and contains(@class, "video")]'
            '//div[contains(@class, "item-img")]/a/@href').getall()
        for scene in scenes:
            # A scene URL carrying the ?nats= affiliate token will not load.
            scene = re.sub(r'\?nats=.*$', '', scene)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//div[contains(@class, "d-lg-block")]/a/div[1]/img[1]/@src')
        if site:
            return match_site(re.search(r'\.com/(.*?)/', site.get()).group(1))
        return "PornMegaLoad"

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        if "?" in item['url']:
            item['url'] = re.search(r'(.*?)\?', item['url']).group(1)
        item['network'] = self.get_network(response)
        item['parent'] = item['site']
        item['type'] = 'Scene'

        checksite = re.sub(r'[^a-z0-9]+', '', item['site'].lower())
        if checksite.lower() not in ["naughtymag", "18eighteen", "bootyliciousmag"]:
            yield self.check_item(item, self.days)

    def get_image(self, response):
        image = super().get_image(response)
        if "base64" in image or "cdn" not in image:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if image:
                image = image.get()
                image = self.format_link(response, image)
        if "_lg" in image:
            image_temp = image.replace("_lg", "_1280")
            if self.check_image(image_temp):
                return image_temp
            image_temp = image.replace("_lg", "_800")
            if self.check_image(image_temp):
                return image_temp
        return image

    def check_image(self, image):
        response = requests.head(image)
        if response.status_code == 200:
            return True
        else:
            return False
