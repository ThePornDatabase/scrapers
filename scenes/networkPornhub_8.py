import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_8Spider(BaseSceneScraper):
    name = 'Pornhub_8'
    network = 'Pornhub'

    # The ModelHub scraper's models, folded in here: modelhub.com 301s to
    # pornhub.com wholesale, so every URL it built landed on the Pornhub home
    # page.  Each slug below was checked against the video grid this spider
    # actually parses -- 12 sit under /model/ and 15 under /pornstar/.  The site
    # names keep ModelHub's "PornHub Premium:" prefix so existing TPDB entries
    # are not split across two names.
    performers = [
        ["/model/anisyia/videos?o=mr&page=%s", "Anisyia", "PornHub Premium: Anisyia"],
        ["/pornstar/brandi-love/videos?o=mr&page=%s", "Brandi Love", "PornHub Premium: Brandi Love"],
        ["/pornstar/britney-amber/videos?o=mr&page=%s", "Britney Amber", "PornHub Premium: Britney Amber"],
        ["/pornstar/cherie-deville/videos?o=mr&page=%s", "Cherie DeVille", "PornHub Premium: Cherie DeVille"],
        ["/pornstar/dani-daniels/videos?o=mr&page=%s", "Dani Daniels", "PornHub Premium: Dani Daniels"],
        ["/model/denata/videos?o=mr&page=%s", "DeNata", "PornHub Premium: DeNata"],
        ["/model/diana-daniels/videos?o=mr&page=%s", "Diana Daniels", "PornHub Premium: Diana Daniels"],
        ["/pornstar/diane-andrews/videos?o=mr&page=%s", "Diane Andrews", "PornHub Premium: Diane Andrews"],
        ["/pornstar/eva-elfie/videos?o=mr&page=%s", "Eva Elfie", "PornHub Premium: Eva Elfie"],
        ["/pornstar/jada-kai/videos?o=mr&page=%s", "Jada Kai", "PornHub Premium: Jada Kai"],
        ["/pornstar/jane-cane/videos?o=mr&page=%s", "Jane Cane", "PornHub Premium: Jane Cane"],
        ["/model/joibae/videos?o=mr&page=%s", "Joibae", "PornHub Premium: Joibae"],
        ["/model/kisankanna/videos?o=mr&page=%s", "kisankanna", "PornHub Premium: kisankanna"],
        ["/model/kriss-kiss/videos?o=mr&page=%s", "Kriss Kiss", "PornHub Premium: Kriss Kiss"],
        ["/pornstar/kyle-balls-wca/videos?o=mr&page=%s", "Kyle Balls WCA", "PornHub Premium: Kyle Balls WCA"],
        ["/pornstar/larkin-love/videos?o=mr&page=%s", "Larkin Love", "PornHub Premium: Larkin Love"],
        ["/pornstar/madeincanarias/videos?o=mr&page=%s", "Madeincanarias", "PornHub Premium: Madeincanarias"],
        ["/pornstar/meana-wolf/videos?o=mr&page=%s", "Meana Wolf", "PornHub Premium: Meana Wolf"],
        ["/pornstar/mia-melano/videos?o=mr&page=%s", "Mia Melano Official", "PornHub Premium: Mia Melano Official"],
        ["/model/mini-diva/videos?o=mr&page=%s", "Mini Diva", "PornHub Premium: Mini Diva"],
        ["/pornstar/miss-banana/videos?o=mr&page=%s", "Miss Banana", "PornHub Premium: Miss Banana"],
        ["/model/missarianaxxx/videos?o=mr&page=%s", "MissArianaxxx", "PornHub Premium: MissArianaxxx"],
        ["/model/princesshaze/videos?o=mr&page=%s", "PrincessHaze", "PornHub Premium: PrincessHaze"],
        ["/model/purple-bitch/videos?o=mr&page=%s", "Purple Bitch", "PornHub Premium: Purple Bitch"],
        ["/model/reislin/videos?o=mr&page=%s", "Reislin", "PornHub Premium: Reislin"],
        ["/model/via-hub/videos?o=mr&page=%s", "Via Hub", "PornHub Premium: Via Hub"],
        ["/pornstar/xev-bellringer/videos?o=mr&page=%s", "Xev Bellringer", "PornHub Premium: Xev Bellringer"],

        # These no longer resolve under any slug variant tried -- each lands on
        # the generic "Top Pornstars and Models" index rather than a profile.
        # Restore with the correct slug if you have it.
        # ["/model/alice-redlips/videos?o=mr&page=%s", "Alice Redlips", "PornHub Premium: Alice Redlips"],  # slug does not resolve
        # ["/model/mila-fox/videos?o=mr&page=%s", "Mila Fox", "PornHub Premium: Mila Fox"],  # slug does not resolve
        # ["/model/morgpie/videos?o=mr&page=%s", "Morgpie", "PornHub Premium: Morgpie"],  # slug does not resolve
        # ["/model/shaiden-rogue/videos?o=mr&page=%s", "Shaiden Rogue", "PornHub Premium: Shaiden Rogue"],  # slug does not resolve
        # ["/model/spring-blooms/videos?o=mr&page=%s", "Spring Blooms", "PornHub Premium: Spring Blooms"],  # slug does not resolve
        # ["/model/taylor-noir/videos?o=mr&page=%s", "Taylor Noir", "PornHub Premium: Taylor Noir"],  # slug does not resolve
        # ["/model/yinyleon/videos?o=mr&page=%s", "Yinyleon", "PornHub Premium: Yinyleon"],  # slug does not resolve
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
