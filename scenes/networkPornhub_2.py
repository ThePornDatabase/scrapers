import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_2Spider(BaseSceneScraper):
    name = 'Pornhub_2'
    network = 'Pornhub'

    performers = [
        ["/pornstar/arabelle-raphael/videos/upload?o=mr&page=%s", "Arabelle Raphael", "Pornhub: Arabelle Raphael"],
        ["/model/ardatb/videos?o=mr&page=%s", "ArdatB", "Pornhub: ArdatB"],
        ["/model/arisuasa/videos?page=%s", "Arisu Asa", "Pornhub: Arisu Asa"],
        ["/model/arrestme/videos?o=mr&page=%s", "ArrestMe", "Pornhub: ArrestMe"],
        ["/model/ashleyaoki/videos?o=mr&page=%s", "Ashley Aoki", "Pornhub: Ashley Aoki"],
        ["/model/asiangoodgirl/videos?o=mr&page=%s", "AsianGoodGirl", "Pornhub: AsianGoodGirl"],
        ["/model/astrodomina/videos?o=mr&page=%s", "AstroDomina", "Pornhub: AstroDomina"],
        ["/pornstar/awesomekate/videos/upload?o=mr&page=%s", "AwesomeKate", "Pornhub: AwesomeKate"],
        ["/pornstar/ayumi-anime/videos/upload?o=mr&page=%s", "Ayumi Anime", "Pornhub: Ayumi Anime"],
        ["/model/baby-montana/videos?page=%s", "Baby Montana", "Pornhub: Baby Montana"],
        ["model/balenci-bby/videos?page=%s", "Balenci BBY", "Pornhub: Balenci BBY"],
        ["/model/banana-nomads/videos?page=%s", "Banana Nomads", "Pornhub: Banana Nomads"],
        ["/model/bigtittygothegg/videos?page=%s", "Big Titty Goth Egg", "Pornhub: Bigtittygothegg"],
        ["/model/broccolibutts/videos?o=mr&page=%s", "Broccolibutts", "Pornhub: Broccolibutts"],
        ["/model/brooke-tilli/videos?page=%s", "Brooke Tilli", "Pornhub: Brooke Tilli"],
        ["/model/carla-cute/videos/upload?o=mr&page=%s", "Carla Cute", "Pornhub: Carla Cute"],
        ["/model/carrylight/videos?o=mr&page=%s", "Carry_Light", "Pornhub: Carry_Light"],
        ["/model/cherry-grace/videos?page=%s", "Cherry Grace", "Pornhub: Cherry Grace"],
        ["/model/chessie-rae/videos/upload?o=mr&page=%s", "Chessie Rae", "Pornhub: Chessie Rae"],
        ["/model/coconey/videos?page=%s", "Coconey", "Pornhub: Coconey"],
        ["/model/cosmicbroccoli/videos/upload?o=mr&page=%s", "Cosmic Broccoli", "Pornhub: Cosmic Broccoli"],
        ["/model/coupleconspiracy/videos?o=mr&page=%s", "CoupleConspiracy", "Pornhub: CoupleConspiracy"],
        ["/users/cathycash/videos/public?page=%s", "Cathy Cravings", "Pornhub: Creampie Cathy"],
        ["/model/creamy-spot/videos/upload?o=mr&page=%s", "Creamy Spot", "Pornhub: Creamy Spot"],
        ["/model/comatozze/videos/upload?o=mr&page=%s", "Cumatozze", "Pornhub: Cumatozze"]
    ]

    selector_map = {
        'title': '//h1[@class="title"]/span/text()',
        'description': '',
        'date': '//script[contains(text(), "@context")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content|//meta[@name="twitter:image"]/@content',
        'tags': '//div[@class="categoriesWrapper"]/a/text()',
        'duration': '//script[contains(text(), "@context")]/text()',
        're_duration': r'duration[\'\"]:.*?[\'\"](.*?)[\'\"]',
        'trailer': '',
        'external_id': r'viewkey=(.*)',
        'pagination': '',
        'type': 'Scene',
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

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    async def start(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True

        for performer in self.performers:
            meta['pagination'] = performer[0]
            meta['initial_performers'] = [performer[1]]
            meta['site'] = performer[2]
            meta['parent'] = "Pornhub"

            link = self.get_next_page_url("https://www.pornhub.com", self.page, meta['pagination'])
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        if "channels" in response.url:
            scenes = response.xpath('//ul[contains(@id, "showAllChanelVideos")]//li[contains(@class, "VideoListItem")]/div/div[@class="phimage"]/a/@href').getall()
        else:
            scenes = response.xpath('//div[contains(@class,"videoUList")]//div[@class="phimage"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        meta = self.copy_meta(response)
        performers = []
        new_perf = response.xpath('//div[contains(@class,"pornstarsWrapper")]/a/@data-mxptext|//div[contains(@class,"pornstarsWrapper")]/a/img/following-sibling::text()[1]')
        if new_perf:
            new_perf = new_perf.getall()
            performers = new_perf
        if meta['initial_performers'][0]:
            if meta['initial_performers'][0] not in performers:
                performers.append(meta['initial_performers'][0])
        return list(map(lambda x: self.cleanup_title(x.strip()), performers))
