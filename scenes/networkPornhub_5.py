import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_5Spider(BaseSceneScraper):
    name = 'Pornhub_5'
    network = 'Pornhub'

    performers = [
        ["/pornstar/madeincanarias/videos?o=mr&page=%s", "Madeincanarias", "Pornhub: Madeincanarias"],
        ["/pornstar/mark-rockwell/videos?o=mr&page=%s", "Mark Rockwell", "Pornhub: Mark Rockwell"],
        ["/model/martina-smith/videos?page=%s", "Martina Smith", "Pornhub: Martina Smith"],
        ["/model/marybarrie/videos/upload?o=mr&page=%s", "Mary Cherry", "Pornhub: MaryBarrie"],
        ["/model/marycherry/videos/upload?o=mr&page=%s", "Mary Cherry", "Pornhub: MaryCherry"],
        ["/model/mayalis/videos?o=mr&page=%s", "Mayalis", "Pornhub: Mayalis"],
        ["/model/michaelfrostpro/videos?page=%s", "Michael Frost", "Pornhub: MichaelFrostPro"],
        ["/model/mickliter/videos?o=mr&page=%s", "MickLiter", "Pornhub: MickLiter"],
        ["/model/mila-solana/videos?page=%s", "Mila Solana", "Pornhub: Mila Solana"],
        ["/model/milfetta/videos?page=%s", "Milfetta", "Pornhub: Milfetta"],
        ["/model/mira-shark/videos/upload?o=mr&page=%s", "Mira Shark", "Pornhub: Mira Shark"],
        ["/model/mirari-hub/videos?o=mr&page=%s", "Mirari", "Pornhub: Mirari"],
        ["/pornstar/miss-alice-wild/videos/upload?o=mr&page=%s", "Alice Wild", "Pornhub: Miss Alice Wild"],
        ["/model/miss-ary/videos?page=%s", "Miss Ary", "Pornhub: Miss Ary"],
        ["/model/miss-ellie-moore/videos?o=mr&page=%s", "Miss Ellie Moore", "Pornhub: Miss Ellie Moore"],
        ["/model/misslexa/videos?o=mr&page=%s", "Miss Lexa", "Pornhub: Miss Lexa"],
        ["/model/morboos/videos?page=%s", "Morboos", "Pornhub: Morboos"],
        ["/model/my_little_betsy/videos?o=mr&page=%s", "My Little Betsy", "Pornhub: My Little Betsy"],
        ["/model/mynaughtyvixen/videos?page=%s", "MyNaughtyVixen", "Pornhub: MyNaughtyVixen"],
        ["/pornstar/mysweetapple/videos/upload?o=mr&page=%s", "MySweetApple", "Pornhub: MySweetApple"],
        ["/model/naty-delgado/videos?page=%s", "Naty Delgado", "Pornhub: Naty Delgado"],
        ["/model/noahpells/videos?page=%s", "Noahpells", "Pornhub: Noahpells"],
        ["/model/nofacegirl/videos/upload?o=mr&page=%s", "Nofacegirl", "Pornhub: Nofacegirl"],
        ["/model/pamsnusnu/videos?page=%s", "Pamsnusnu", "Pornhub: Pamsnusnu"],
        ["/model/panamero-088/videos?page=%s", "Panamero 088", "Pornhub: Panamero 088"]
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
