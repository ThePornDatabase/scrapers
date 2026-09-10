import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhub_1Spider(BaseSceneScraper):
    name = 'Pornhub_1'
    network = 'Pornhub'

    performers = [
        ["/model/18_yoyo/videos?o=mr&page=%s", "18_yoyo", "Pornhub: 18_yoyo"],
        ["/model/1twothreecum/videos/upload?o=mr&page=%s", "", "Pornhub: 1twothreecum"],
        ["/model/404hotfound/videos?o=mr&page=%s", "404HotFound", "Pornhub: 404HotFound"],
        ["/pornstar/adriana-chechik/videos/upload?o=mr&page=%s", "Adriana Chechik", "Pornhub: Adriana Chechik"],
        ["/model/aeries-steele/videos/upload?o=mr&page=%s", "Aeries Steele", "Pornhub: Aeries Steele"],
        ["/model/aestra-azure/videos/upload?o=mr&page=%s", "Aestra Azure", "Pornhub: Aestra Azure"],
        ["/model/agataruiz/videos?page=%s", "Agata Ruiz", "Pornhub: Agata Ruiz"],
        ["/model/ailish/videos?o=mr&page=%s", "Ailish", "Pornhub: Ailish"],
        ["/model/alaska-zade/videos?page=%s", "Alaska Zade", "Pornhub: Alaska Zade"],
        ["/pornstar/alex-adams/videos/upload?o=mr&page=%s", "Alex Adams", "Pornhub: Alex Adams"],
        ["/pornstar/alex-de-la-flor/videos/upload?o=mr&page=%s", "Alex De La Flor", "Pornhub: Alex De La Flor"],
        ["/model/alina-rai/videos?o=mr&page=%s", "Alina Rai", "Pornhub: Alina Rai"],
        ["/model/alina_rose/videos?o=mr&page=%s", "Alina Rose", "Pornhub: Alina Rose"],
        ["/pornstar/alison-rey/videos/upload?o=mr&page=%s", "Alison Rey", "Pornhub: Alison Rey"],
        ["/model/allinika/videos?o=mr&page=%s", "Allinika", "Pornhub: Allinika"],
        ["/model/almondbabe/videos?o=mr&page=%s", "AlmondBabe", "Pornhub: AlmondBabe"],
        ["/model/amadani/videos?o=mr&page=%s", "Amadani", "Pornhub: Amadani"],
        ["/model/andreylov91/videos?o=mr&page=%s", "AndreyLov91", "Pornhub: AndreyLov91"],
        ["/model/angelssex/videos?o=mr&page=%s", "Angelssex", "Pornhub: Angelssex"],
        ["/model/anika-spring/videos?o=mr&page=%s", "Anika Spring", "Pornhub: Anika Spring"],
        ["/model/anna-liisppb/videos?o=mr&page=%s", "Anna Liisppb", "Pornhub: Anna Liisppb"],
        ["/model/annie-may-may/videos?o=mr&page=%s", "Annie May May", "Pornhub: Annie May May"],
        ["/model/anntall/videos?page=%s", "Anntall", "Pornhub: Anntall"],
        ["/model/anny-walker/videos?o=mr&page=%s", "Anny Walker", "Pornhub: Anny Walker"],
        ["/model/april-eighteen/videos?o=mr&page=%s", "April Eighteen", "Pornhub: April Eighteen"]
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
