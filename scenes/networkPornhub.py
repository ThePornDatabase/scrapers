import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhubSpider(BaseSceneScraper):
    name = 'Pornhub'
    network = 'Pornhub'

    performers = [
        ["/channels/pornhub-originals-vr?o=mr&page=%s", "", "Pornhub: Pornhub Originals VR"],
        ["/model/404hotfound/videos?o=mr&page=%s", "404HotFound", "Pornhub: 404HotFound"],
        ["/model/aestra-azure/videos/upload?o=mr&page=%s", "Aestra Azure", "Pornhub: Aestra Azure"],
        ["/model/agataruiz/videos?page=%s", "Agata Ruiz", "Pornhub: Agata Ruiz"],
        ["/model/ailish/videos?o=mr&page=%s", "Ailish", "Pornhub: Ailish"],
        ["/model/alaska-zade/videos?page=%s", "Alaska Zade", "Pornhub: Alaska Zade"],
        ["/model/alina-rai/videos?o=mr&page=%s", "Alina Rai", "Pornhub: Alina Rai"],
        ["/model/alina_rose/videos?o=mr&page=%s", "Alina Rose", "Pornhub: Alina Rose"],
        ["/model/allinika/videos?o=mr&page=%s", "Allinika", "Pornhub: Allinika"],
        ["/model/almondbabe/videos?o=mr&page=%s", "AlmondBabe", "Pornhub: AlmondBabe"],
        ["/model/amadani/videos?o=mr&page=%s", "Amadani", "Pornhub: Amadani"],
        ["/model/andreylov91/videos?o=mr&page=%s", "AndreyLov91", "Pornhub: AndreyLov91"],
        ["/model/anika-spring/videos?o=mr&page=%s", "Anika Spring", "Pornhub: Anika Spring"],
        ["/model/anna-liisppb/videos?o=mr&page=%s", "Anna Liisppb", "Pornhub: Anna Liisppb"],
        ["/model/anntall/videos?page=%s", "Anntall", "Pornhub: Anntall"],
        ["/model/anny-walker/videos?o=mr&page=%s", "Anny Walker", "Pornhub: Anny Walker"],
        ["/model/april-eighteen/videos?o=mr&page=%s", "April Eighteen", "Pornhub: April Eighteen"],
        ["/model/ardatb/videos?o=mr&page=%s", "ArdatB", "Pornhub: ArdatB"],
        ["/model/arisuasa/videos?page=%s", "Arisu Asa", "Pornhub: Arisu Asa"],
        ["/model/arrestme/videos?o=mr&page=%s", "ArrestMe", "Pornhub: ArrestMe"],
        ["/model/ashleyaoki/videos?o=mr&page=%s", "Ashley Aoki", "Pornhub: Ashley Aoki"],
        ["/model/asiangoodgirl/videos?o=mr&page=%s", "AsianGoodGirl", "Pornhub: AsianGoodGirl"],
        ["/model/astrodomina/videos?o=mr&page=%s", "AstroDomina", "Pornhub: AstroDomina"],
        ["/model/banana-nomads/videos?page=%s", "Banana Nomads", "Pornhub: Banana Nomads"],
        ["/model/bigtittygothegg/videos?page=%s", "Big Titty Goth Egg", "Pornhub: Bigtittygothegg"],
        ["/model/coconey/videos?page=%s", "Coconey", "Pornhub: Coconey"],
        ["/model/coupleconspiracy/videos?o=mr&page=%s", "CoupleConspiracy", "Pornhub: CoupleConspiracy"],
        ["/model/daniela-antury/videos?page=%s", "Daniela Antury", "Pornhub: Daniela Antury"],
        ["/model/dutchboy2303/videos?page=%s", "Dutchboy2303", "Pornhub: Dutchboy2303"],
        ["/model/ellakojiro/videos?page=%s", "Ella Kojiro", "Pornhub: Ella Kojiro"],
        ["/model/emma-fiore/videos?page=%s", "Emma Fiore", "Pornhub: Emma Fiore"],
        ["/model/fuckforeverever/videos?page=%s", "Fuckforeverever", "Pornhub: Fuckforeverever"],
        ["/model/gentlyperv/videos?o=mr&page=%s", "GentlyPerv", "Pornhub: GentlyPerv"],
        ["/model/harperthefox/videos?o=mr&page=%s", "HarperTheFox", "Pornhub: HarperTheFox"],
        ["/model/helloelly/videos?o=mr&page=%s", "HelloElly", "Pornhub: HelloElly"],
        ["/model/joey-lee/videos?o=mr&page=%s", "Joey Lee", "Pornhub: Joey Lee"],
        ["/model/kelly-aleman/videos?o=mr&page=%s", "Kelly Aleman", "Pornhub: Kelly Aleman"],
        ["/model/loly-lips/videos?o=mr&page=%s", "Loly Lips", "Pornhub: Loly Lips"],
        ["/model/luna-okko/videos?o=mr&page=%s", "Luna Okko", "Pornhub: Luna Okko"],
        ["/model/luxury-tumanova-woman/videos?o=mr&page=%s", "Alina Tumanova", "Pornhub: Luxury Tumanova Woman"],
        ["/model/mad_bros/videos?page=%s", "Mad_Bros", "Pornhub: Mad_Bros"],
        ["/model/martina-smith/videos?page=%s", "Martina Smith", "Pornhub: Martina Smith"],
        ["/model/milfetta/videos?page=%s", "Milfetta", "Pornhub: Milfetta"],
        ["/model/mynaughtyvixen/videos?page=%s", "MyNaughtyVixen", "Pornhub: MyNaughtyVixen"],
        ["/model/pamsnusnu/videos?page=%s", "Pamsnusnu", "Pornhub: Pamsnusnu"],
        ["/model/pinaxpress/videos?page=%s", "PinaXpress", "Pornhub: PinaXpress"],
        ["/model/pure-pleasure/videos?page=%s", "Pure Pleasure", "Pornhub: Pure Pleasure"],
        ["/model/reels_plans/videos?o=mr&page=%s", "Reels Plans", "Pornhub: Reels Plans"],
        ["/model/serenity-cox/videos?o=mr&page=%s", "Serenity Cox", "Pornhub: Serenity Cox"],
        ["/model/siasiberia/videos?page=%s", "Sia Siberia", "Pornhub: Sia Siberia"],
        ["/model/sweetie-fox/videos?page=%s", "Sweetie Fox", "Pornhub: Sweetie Fox"],
        ["/model/yinyleon/videos?page=%s", "Yinyleon", "Pornhub: Yinyleon"],
        ["/model/your_father_secret/videos?page=%s", "Your_father_secret", "Pornhub: Your_father_secret"],
        ["/model/zirael_rem/videos?page=%s", "Zirael_Rem", "Pornhub: Zirael_Rem"],
        ["/pornstar/adriana-chechik/videos/upload?o=mr&page=%s", "Adriana Chechik", "Pornhub: Adriana Chechik"],
        ["/pornstar/alex-adams/videos/upload?o=mr&page=%s", "Alex Adams", "Pornhub: Alex Adams"],
        ["/pornstar/alex-de-la-flor/videos/upload?o=mr&page=%s", "Alex De La Flor", "Pornhub: Alex De La Flor"],
        ["/pornstar/alison-rey/videos/upload?o=mr&page=%s", "Alison Rey", "Pornhub: Alison Rey"],
        ["/pornstar/arabelle-raphael/videos/upload?o=mr&page=%s", "Arabelle Raphael", "Pornhub: Arabelle Raphael"],
        ["/pornstar/awesomekate/videos/upload?o=mr&page=%s", "AwesomeKate", "Pornhub: AwesomeKate"],
        ["/pornstar/ayumi-anime/videos/upload?o=mr&page=%s", "Ayumi Anime", "Pornhub: Ayumi Anime"],
        ["/pornstar/dan-dangler/videos/upload?page=%s", "Dan Dangler", "Pornhub: Dan Dangler"],
        ["/pornstar/danika-mori/videos/upload?o=mr&page=%s", "Danika Mori", "Pornhub: Danika Mori"],
        ["/pornstar/eva-elfie/videos/upload?o=mr&page=%s", "Eva Elfie", "Pornhub: Eva Elfie"],
        ["/pornstar/hailey-rose/videos/upload?o=mr&page=%s", "Hailey Rose", "Pornhub: Hailey Rose"],
        ["/pornstar/heather-kane/videos/upload?o=mr&page=%s", "Heather Kane", "Pornhub: Heather Kane"],
        ["/pornstar/madeincanarias/videos?o=mr&page=%s", "Madeincanarias", "Pornhub: Madeincanarias"],
        ["/pornstar/mark-rockwell/videos?o=mr&page=%s", "Mark Rockwell", "Pornhub: Mark Rockwell"],
        ["/pornstar/miss-alice-wild/videos/upload?o=mr&page=%s", "Alice Wild", "Pornhub: Miss Alice Wild"],
        ["/pornstar/snow-deville/videos/upload?page=%s", "Snow Deville", "Pornhub: Snow Deville"],
        ["/users/cathycash/videos/public?page=%s", "Cathy Cravings", "Pornhub: Creampie Cathy"],
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

    def start_requests(self):
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
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        if "channels" in response.url:
            scenes = response.xpath('//ul[contains(@id, "showAllChanelVideos")]//li[contains(@class, "VideoListItem")]/div/div[@class="phimage"]/a/@href').getall()
        else:
            scenes = response.xpath('//div[contains(@class,"videoUList")]//div[@class="phimage"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        meta = response.meta
        performers = []
        new_perf = response.xpath('//div[contains(@class,"pornstarsWrapper")]/a/@data-mxptext|//div[contains(@class,"pornstarsWrapper")]/a/img/following-sibling::text()[1]')
        if new_perf:
            new_perf = new_perf.getall()
            performers = new_perf
        if meta['initial_performers'][0]:
            if meta['initial_performers'][0] not in performers:
                performers.append(meta['initial_performers'][0])
        return list(map(lambda x: self.cleanup_title(x.strip()), performers))
