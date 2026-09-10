import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_4Spider(BaseSceneScraper):
    name = 'Pornhub_4'
    network = 'Pornhub'

    performers = [
        ["/model/hotlovers420/videos?o=mr&page=%s", "Mia Stark", "Pornhub: Hotlovers420"],
        ["/model/house-of-era/videos?o=mr&page=%s", "House of Era", "Pornhub: House of Era"],
        ["/model/jean-summer/videos/upload?o=mr&page=%s", "Jean Summer", "Pornhub: Jean Summer"],
        ["/model/jellyfilledgirls/videos/upload?o=mr&page=%s", "JellyfilledGirls", "Pornhub: JellyfilledGirls"],
        ["/model/joey-lee/videos?o=mr&page=%s", "Joey Lee", "Pornhub: Joey Lee"],
        ["/model/john-and-sky/videos/upload?o=mr&page=%s", "", "Pornhub: John and Sky"],
        ["/model/kakao_chan/videos?o=mr&page=%s", "kakao_chan", "Pornhub: kakao_chan"],
        ["/model/kate-marley/videos?o=mr&page=%s", "Kate Marley", "Pornhub: Kate Marley"],
        ["/model/kelly-aleman/videos?o=mr&page=%s", "Kelly Aleman", "Pornhub: Kelly Aleman"],
        ["/model/knock-knock-club/videos?o=mr&page=%s", "Knock Knock Club", "Pornhub: Knock Knock Club"],
        ["/model/lacyluxxx/videos?o=mr&page=%s", "Lacy Luxxx", "Pornhub: Lacy Luxxx"],
        ["/model/lama-grey/videos?o=mr&page=%s", "Hiyouth", "Pornhub: Lama Grey"],
        ["/model/lexisstar/videos?o=mr&page=%s", "Lexis Star", "Pornhub: Lexis Star"],
        ["/model/lil-karina/videos/upload?o=mr&page=%s", "Lil Karina", "Pornhub: Lil Karina"],
        ["/model/lina-moore/videos?o=mr&page=%s", "Lina Moore", "Pornhub: Lina Moore"],
        ["/pornstar/lindsey-love/videos/upload?o=mr&page=%s", "Lindsey Love", "Pornhub: Lindsey Love"],
        ["/model/lis-evans/videos/upload?o=mr&page=%s", "Lis Evans", "Pornhub: Lis Evans"],
        ["/model/loly-lips/videos?o=mr&page=%s", "Loly Lips", "Pornhub: Loly Lips"],
        ["/model/loly-nebel/videos/upload?o=mr&page=%s", "Loly Nebel", "Pornhub: Loly Nebel"],
        ["/model/lucas-and-daisy/videos/upload?o=mr&page=%s", "Lucas and Daisy", "Pornhub: Lucas and Daisy"],
        ["/model/luna-okko/videos?o=mr&page=%s", "Luna Okko", "Pornhub: Luna Okko"],
        ["/model/luna-vitaler/videos/upload?o=mr&page=%s", "Luna Vitaler", "Pornhub: Luna Vitaler"],
        ["/model/luxury-girl/videos?o=mr&page=%s", "Luxury Girl", "Pornhub: Luxury Girl"],
        ["/model/luxury-tumanova-woman/videos?o=mr&page=%s", "Alina Tumanova", "Pornhub: Luxury Tumanova Woman"],
        ["/model/mad_bros/videos?page=%s", "Mad_Bros", "Pornhub: Mad_Bros"]
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
