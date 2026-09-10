import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkFaphouseSpider(BaseSceneScraper):
    name = 'Faphouse'

    # network is deliberately NOT a class attribute: BaseSceneScraper prefers
    # self.network over response.meta, so a class-level value would override the
    # per-row network below. start() puts it in meta instead, defaulting to
    # "Faphouse" so the rows that do not name one behave exactly as before.
    #
    # Row format: [path, initial performer, site, parent (optional), network (optional)]
    performers = [
        ["/transgender/models/lucie-arztin?page=%s", "Lucie Arztin", "Faphouse: Lucie Arztin"],
        ["/models/wanilianna?page=%s", "Wanilianna", "Faphouse: Wanilianna"],
        ["/models/karinalin?page=%s", "Karina Lin2", "Faphouse: Karina Lin"],
        ["/models/lucie-arztin?page=%s", "", "Faphouse: Twistedrama"],
        ["/studios/african-sex-trip?page=%s", "", "Faphouse: African Sex Trip"],
        ["/studios/boymeetsmilf?page=%s", "", "Faphouse: Boy Meets MILF"],
        ["/pornstars/angel-youngs?page=%s", "", "Faphouse: Angel Youngs"],
        ["/models/spiel-maschinerie?page=%s", "", "Faphouse: Spiel Maschinerie"],
        # ErosArts tours geo/VPN-block this exit, but FapHouse carries two of them
        # under their own source domains. Kept on the ErosArts names so the scenes
        # land on the existing entries rather than new "Faphouse: ..." ones.
        ["/studios/eros-joi?page=%s", "", "Jerk Off Instructions", "Jerk Off Instructions", "Eros Arts"],
        ["/studios/taboo-handjobs?page=%s", "", "Taboo Handjobs", "Taboo Handjobs", "Eros Arts"],
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[contains(@class, "__description")]/details/p/text()',
        'date': '//span[contains(@class, "publish-date")]/text()',
        're_date': r'(\d{2}\.\d{2}\.\d{4})',
        'date_formats': ['%d.%m.%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "video-info-details")]//a[@class="vid-c" and contains(@href, "/videos")]/text()',
        'duration': '//span[contains(@class,"_video-duration")]/text()',
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
            meta['parent'] = performer[3] if len(performer) > 3 else "Faphouse"
            meta['network'] = performer[4] if len(performer) > 4 else "Faphouse"

            link = self.get_next_page_url("https://faphouse.com", self.page, meta['pagination'])
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
        scenes = response.xpath('//div[contains(@class, "thumb tv")]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-id').get()

            scene = scene.xpath('./div[1]/a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        meta = self.copy_meta(response)
        performers = []
        new_perf = response.xpath('//div[contains(@class,"pornstarsWrapper")]/a/@data-mxptext|//div[contains(@class,"pornstarsWrapper")]/a/img/following-sibling::text()[1]')
        if not new_perf:
            new_perf = response.xpath('//div[contains(@class, "video-info-details__categories")]//a[contains(@href, "/pornstars") or contains(@href, "/models/")]/span[contains(@class, "title")]/text()')
        if new_perf:
            new_perf = new_perf.getall()
            performers = new_perf
        if meta['initial_performers'][0]:
            if meta['initial_performers'][0] not in performers:
                performers.append(meta['initial_performers'][0])
        return list(map(lambda x: self.cleanup_title(x.strip()), performers))
