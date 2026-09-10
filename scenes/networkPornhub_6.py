import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_6Spider(BaseSceneScraper):
    name = 'Pornhub_6'
    network = 'Pornhub'

    performers = [
        ["/model/parrotgirl/videos?page=%s", "ParrotGirl", "Pornhub: ParrotGirl"],
        ["/model/pinaxpress/videos?page=%s", "PinaXpress", "Pornhub: PinaXpress"],
        ["/channels/pornhub-originals-vr?o=mr&page=%s", "", "Pornhub: Pornhub Originals VR"],
        ["/model/princess-alice/videos?o=mr&page=%s", "Princess Alice", "Pornhub: Princess Alice"],
        ["/model/pure-pleasure/videos?page=%s", "Pure Pleasure", "Pornhub: Pure Pleasure"],
        ["/model/rainontheridge/videos?o=mr&page=%s", "RainOnTheRidge", "Pornhub: RainOnTheRidge"],
        ["/model/reels_plans/videos?o=mr&page=%s", "Reels Plans", "Pornhub: Reels Plans"],
        ["/model/rina_vlog/videos?o=mr&page=%s", "Rina_Vlog", "Pornhub: Rina_Vlog"],
        ["/model/serenity-cox/videos?o=mr&page=%s", "Serenity Cox", "Pornhub: Serenity Cox"],
        ["/model/siasiberia/videos?page=%s", "Sia Siberia", "Pornhub: Sia Siberia"],
        ["/model/slemgem/videos?page=%s", "Slemgem", "Pornhub: Slemgem"],
        ["/pornstar/snow-deville/videos/upload?page=%s", "Snow Deville", "Pornhub: Snow Deville"],
        ["/model/solazola/videos?o=mr&page=%s", "Sola Zola", "Pornhub: Sola Zola"],
        ["/model/sonyagold/videos?page=%s", "Sonya Gold", "Pornhub: Sonya Gold"],
        ["/model/sweetherry/videos?o=mr&page=%s", "SweetHerry", "Pornhub: SweetHerry"],
        ["/model/sweetie-fox/videos?page=%s", "Sweetie Fox", "Pornhub: Sweetie Fox"],
        ["/pornstar/swife-katy/videos/upload?o=mr&page=%s", "SWife Katy", "Pornhub: SWife Katy"],
        ["/model/tara-rico/videos?page=%s", "Tara Rico", "Pornhub: Tara Rico"],
        ["/model/teddy-tarantino/videos/upload?o=mr&page=%s", "Teddy Tarantino", "Pornhub: Teddy Tarantino"],
        ["/model/thestartofus/videos/upload?o=mr&page=%s", "Adhara Skai", "Pornhub: TheStartofUs"],
        ["/pornstar/tru-kait/videos/upload?o=mr&page=%s", "Tru Kait", "Pornhub: Tru Kait"],
        ["/model/verobuffone/videos?page=%s", "Verobuffone", "Pornhub: Verobuffone"],
        ["/model/verysexydasha/videos?o=mr&page=%s", "Very Sexy Dasha", "Pornhub: Very Sexy Dasha"],
        ["/model/vincent_vega_off/videos?o=mr&page=%s", "vincent_vega_off", "Pornhub: vincent_vega_off"],
        ["/model/yinyleon/videos?page=%s", "Yinyleon", "Pornhub: Yinyleon"]
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
