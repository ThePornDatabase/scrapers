import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_3Spider(BaseSceneScraper):
    name = 'Pornhub_3'
    network = 'Pornhub'

    performers = [
        ["/model/cyberlycrush/videos?o=mr&page=%s", "Cyberly Crush", "Pornhub: Cyberly Crush"],
        ["/pornstar/dan-dangler/videos/upload?page=%s", "Dan Dangler", "Pornhub: Dan Dangler"],
        ["/model/daniela-antury/videos?page=%s", "Daniela Antury", "Pornhub: Daniela Antury"],
        ["/pornstar/danika-mori/videos/upload?o=mr&page=%s", "Danika Mori", "Pornhub: Danika Mori"],
        ["/model/daphanez/videos?page=%s", "DaPhaneZ", "Pornhub: DaPhaneZ"],
        ["/model/deltongirl/videos?page=%s", "DeltonGirl", "Pornhub: DeltonGirl"],
        ["/model/domslutfucker/videos?page=%s", "Domslutfucker", "Pornhub: DomSlutFucker"],
        ["/model/dutchboy2303/videos?page=%s", "Dutchboy2303", "Pornhub: Dutchboy2303"],
        ["/model/ellakojiro/videos?page=%s", "Ella Kojiro", "Pornhub: Ella Kojiro"],
        ["/model/emiliabunny/videos?o=mr&page=%s", "Emilia Bunny", "Pornhub: Emilia Bunny"],
        ["/model/emilia-shot/videos/upload?o=mr&page=%s", "Emilia Shot", "Pornhub: Emilia Shot"],
        ["/model/emma-fiore/videos?page=%s", "Emma Fiore", "Pornhub: Emma Fiore"],
        ["/pornstar/eva-elfie/videos/upload?o=mr&page=%s", "Eva Elfie", "Pornhub: Eva Elfie"],
        ["/model/fantasybabe/videos/upload?o=mr&page=%s", "Fantasy Babe", "Pornhub: Fantasy Babe"],
        ["/model/fleamx/videos?o=mr&page=%s", "Fleamx", "Pornhub: fleamx"],
        ["/pornstar/freckledred/videos/upload?o=mr&page=%s", "FreckledRed", "Pornhub: FreckledRED"],
        ["/model/fuckforeverever/videos?page=%s", "Fuckforeverever", "Pornhub: Fuckforeverever"],
        ["/model/gentlyperv/videos?o=mr&page=%s", "GentlyPerv", "Pornhub: GentlyPerv"],
        ["/model/goddess-lucie/videos?o=mr&page=%s", "Goddess Lucie", "Pornhub: Goddess Lucie"],
        ["/model/guesswhox2/videos?o=mr&page=%s", "GuessWhoX2", "Pornhub: GuessWhoX2"],
        ["/pornstar/hailey-rose/videos/upload?o=mr&page=%s", "Hailey Rose", "Pornhub: Hailey Rose"],
        ["/model/harperthefox/videos?o=mr&page=%s", "HarperTheFox", "Pornhub: HarperTheFox"],
        ["/pornstar/heather-kane/videos/upload?o=mr&page=%s", "Heather Kane", "Pornhub: Heather Kane"],
        ["/model/helloelly/videos?o=mr&page=%s", "HelloElly", "Pornhub: HelloElly"],
        ["/model/hiyouth/videos?o=mr&page=%s", "Hiyouth", "Pornhub: Hiyouth"]
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
