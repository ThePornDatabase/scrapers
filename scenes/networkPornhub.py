import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPornhubSpider(BaseSceneScraper):
    name = 'Pornhub'
    network = 'Pornhub'

    performers = [
        ["/channels/pornhub-originals-vr?o=mr&page=%s", "", "Pornhub: Pornhub Originals VR"],
        ["/model/sweetherry/videos?o=mr&page=%s", "SweetHerry", "Pornhub: SweetHerry"],
        ["/model/404hotfound/videos?o=mr&page=%s", "404HotFound", "Pornhub: 404HotFound"],
        ["/model/aeries-steele/videos/upload?o=mr&page=%s", "Aeries Steele", "Pornhub: Aeries Steele"],
        ["/model/aestra-azure/videos/upload?o=mr&page=%s", "Aestra Azure", "Pornhub: Aestra Azure"],
        ["/model/agataruiz/videos?page=%s", "Agata Ruiz", "Pornhub: Agata Ruiz"],
        ["/model/ailish/videos?o=mr&page=%s", "Ailish", "Pornhub: Ailish"],
        ["/model/alaska-zade/videos?page=%s", "Alaska Zade", "Pornhub: Alaska Zade"],
        ["/model/alina-rai/videos?o=mr&page=%s", "Alina Rai", "Pornhub: Alina Rai"],
        ["/model/alina_rose/videos?o=mr&page=%s", "Alina Rose", "Pornhub: Alina Rose"],
        ["/model/allinika/videos?o=mr&page=%s", "Allinika", "Pornhub: Allinika"],
        ["/model/almondbabe/videos?o=mr&page=%s", "AlmondBabe", "Pornhub: AlmondBabe"],
        ["/model/amadani/videos?o=mr&page=%s", "Amadani", "Pornhub: Amadani"],
        ["/model/angelssex/videos?o=mr&page=%s", "Angelssex", "Pornhub: Angelssex"],
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
        ["/model/baby-montana/videos?page=%s", "Baby Montana", "Pornhub: Baby Montana"],
        ["/model/banana-nomads/videos?page=%s", "Banana Nomads", "Pornhub: Banana Nomads"],
        ["/model/bigtittygothegg/videos?page=%s", "Big Titty Goth Egg", "Pornhub: Bigtittygothegg"],
        ["/model/brooke-tilli/videos?page=%s", "Brooke Tilli", "Pornhub: Brooke Tilli"],
        ["/model/coconey/videos?page=%s", "Coconey", "Pornhub: Coconey"],
        ["/model/coupleconspiracy/videos?o=mr&page=%s", "CoupleConspiracy", "Pornhub: CoupleConspiracy"],
        ["/model/daniela-antury/videos?page=%s", "Daniela Antury", "Pornhub: Daniela Antury"],
        ["/model/daphanez/videos?page=%s", "DaPhaneZ", "Pornhub: DaPhaneZ"],
        ["/model/deltongirl/videos?page=%s", "DeltonGirl", "Pornhub: DeltonGirl"],
        ["/model/domslutfucker/videos?page=%s", "Domslutfucker", "Pornhub: DomSlutFucker"],
        ["/model/dutchboy2303/videos?page=%s", "Dutchboy2303", "Pornhub: Dutchboy2303"],
        ["/model/ellakojiro/videos?page=%s", "Ella Kojiro", "Pornhub: Ella Kojiro"],
        # ["/model/elly-clutch/videos?page=%s", "Elly Clutch", "Pornhub: Elly Clutch"], Disabled in leiu of ManyVids
        ["/model/emma-fiore/videos?page=%s", "Emma Fiore", "Pornhub: Emma Fiore"],
        ["/model/fuckforeverever/videos?page=%s", "Fuckforeverever", "Pornhub: Fuckforeverever"],
        ["/model/gentlyperv/videos?o=mr&page=%s", "GentlyPerv", "Pornhub: GentlyPerv"],
        ["/model/harperthefox/videos?o=mr&page=%s", "HarperTheFox", "Pornhub: HarperTheFox"],
        ["/model/helloelly/videos?o=mr&page=%s", "HelloElly", "Pornhub: HelloElly"],
        ["/model/hotlovers420/videos?o=mr&page=%s", "Mia Stark", "Pornhub: Hotlovers420"],
        ["/model/joey-lee/videos?o=mr&page=%s", "Joey Lee", "Pornhub: Joey Lee"],
        ["/model/kate-marley/videos?o=mr&page=%s", "Kate Marley", "Pornhub: Kate Marley"],
        ["/model/kelly-aleman/videos?o=mr&page=%s", "Kelly Aleman", "Pornhub: Kelly Aleman"],
        ["/model/knock-knock-club/videos?o=mr&page=%s", "Knock Knock Club", "Pornhub: Knock Knock Club"],
        ["/model/lexisstar/videos?o=mr&page=%s", "Lexis Star", "Pornhub: Lexis Star"],
        ["/model/loly-lips/videos?o=mr&page=%s", "Loly Lips", "Pornhub: Loly Lips"],
        ["/model/luna-okko/videos?o=mr&page=%s", "Luna Okko", "Pornhub: Luna Okko"],
        ["/model/luxury-girl/videos?o=mr&page=%s", "Luxury Girl", "Pornhub: Luxury Girl"],
        ["/model/luxury-tumanova-woman/videos?o=mr&page=%s", "Alina Tumanova", "Pornhub: Luxury Tumanova Woman"],
        ["/model/mad_bros/videos?page=%s", "Mad_Bros", "Pornhub: Mad_Bros"],
        ["/model/martina-smith/videos?page=%s", "Martina Smith", "Pornhub: Martina Smith"],
        ["/model/michaelfrostpro/videos?page=%s", "Michael Frost", "Pornhub: MichaelFrostPro"],
        ["/model/miss-ary/videos?page=%s", "Miss Ary", "Pornhub: Miss Ary"],
        ["/model/mila-solana/videos?page=%s", "Mila Solana", "Pornhub: Mila Solana"],
        ["/model/milfetta/videos?page=%s", "Milfetta", "Pornhub: Milfetta"],
        ["/model/morboos/videos?page=%s", "Morboos", "Pornhub: Morboos"],
        ["/model/mynaughtyvixen/videos?page=%s", "MyNaughtyVixen", "Pornhub: MyNaughtyVixen"],
        ["/model/naty-delgado/videos?page=%s", "Naty Delgado", "Pornhub: Naty Delgado"],
        ["/model/noahpells/videos?page=%s", "Noahpells", "Pornhub: Noahpells"],
        ["/model/pamsnusnu/videos?page=%s", "Pamsnusnu", "Pornhub: Pamsnusnu"],
        ["/model/panamero-088/videos?page=%s", "Panamero 088", "Pornhub: Panamero 088"],
        ["/model/parrotgirl/videos?page=%s", "ParrotGirl", "Pornhub: ParrotGirl"],
        ["/model/pinaxpress/videos?page=%s", "PinaXpress", "Pornhub: PinaXpress"],
        ["/model/pure-pleasure/videos?page=%s", "Pure Pleasure", "Pornhub: Pure Pleasure"],
        ["/model/rainontheridge/videos?o=mr&page=%s", "RainOnTheRidge", "Pornhub: RainOnTheRidge"],
        ["/model/reels_plans/videos?o=mr&page=%s", "Reels Plans", "Pornhub: Reels Plans"],
        ["/model/rina_vlog/videos?o=mr&page=%s", "Rina_Vlog", "Pornhub: Rina_Vlog"],
        ["/model/serenity-cox/videos?o=mr&page=%s", "Serenity Cox", "Pornhub: Serenity Cox"],
        ["/model/siasiberia/videos?page=%s", "Sia Siberia", "Pornhub: Sia Siberia"],
        ["/model/slemgem/videos?page=%s", "Slemgem", "Pornhub: Slemgem"],
        ["/model/sonyagold/videos?page=%s", "Sonya Gold", "Pornhub: Sonya Gold"],
        ["model/balenci-bby/videos?page=%s", "Balenci BBY", "Pornhub: Balenci BBY"],
        ["/model/sweetie-fox/videos?page=%s", "Sweetie Fox", "Pornhub: Sweetie Fox"],
        ["/model/tara-rico/videos?page=%s", "Tara Rico", "Pornhub: Tara Rico"],
        ["/model/yinyleon/videos?page=%s", "Yinyleon", "Pornhub: Yinyleon"],
        ["/model/your_father_secret/videos?page=%s", "Your_father_secret", "Pornhub: Your_father_secret"],
        ["/model/verobuffone/videos?page=%s", "Verobuffone", "Pornhub: Verobuffone"],
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
        ["/pornstar/freckledred/videos/upload?o=mr&page=%s", "FreckledRed", "Pornhub: FreckledRED"],
        ["/pornstar/hailey-rose/videos/upload?o=mr&page=%s", "Hailey Rose", "Pornhub: Hailey Rose"],
        ["/pornstar/heather-kane/videos/upload?o=mr&page=%s", "Heather Kane", "Pornhub: Heather Kane"],
        ["/pornstar/madeincanarias/videos?o=mr&page=%s", "Madeincanarias", "Pornhub: Madeincanarias"],
        ["/pornstar/mark-rockwell/videos?o=mr&page=%s", "Mark Rockwell", "Pornhub: Mark Rockwell"],
        ["/pornstar/miss-alice-wild/videos/upload?o=mr&page=%s", "Alice Wild", "Pornhub: Miss Alice Wild"],
        ["/pornstar/snow-deville/videos/upload?page=%s", "Snow Deville", "Pornhub: Snow Deville"],
        ["/users/cathycash/videos/public?page=%s", "Cathy Cravings", "Pornhub: Creampie Cathy"],
        ["/model/cherry-grace/videos?page=%s", "Cherry Grace", "Pornhub: Cherry Grace"],
        ["/pornstar/lindsey-love/videos/upload?o=mr&page=%s", "Lindsey Love", "Pornhub: Lindsey Love"],
        ["/pornstar/mysweetapple/videos/upload?o=mr&page=%s", "MySweetApple", "Pornhub: MySweetApple"],
        ["/model/lucas-and-daisy/videos/upload?o=mr&page=%s", "Lucas and Daisy", "Pornhub: Lucas and Daisy"],
        ["/model/cosmicbroccoli/videos/upload?o=mr&page=%s", "Cosmic Broccoli", "Pornhub: Cosmic Broccoli"],
        ["/model/thestartofus/videos/upload?o=mr&page=%s", "Adhara Skai", "Pornhub: TheStartofUs"],
        ["/model/jellyfilledgirls/videos/upload?o=mr&page=%s", "JellyfilledGirls", "Pornhub: JellyfilledGirls"],
        ["/model/carla-cute/videos/upload?o=mr&page=%s", "Carla Cute", "Pornhub: Carla Cute"],
        ["/model/creamy-spot/videos/upload?o=mr&page=%s", "Creamy Spot", "Pornhub: Creamy Spot"],
        ["/model/chessie-rae/videos/upload?o=mr&page=%s", "Chessie Rae", "Pornhub: Chessie Rae"],
        ["/model/nofacegirl/videos/upload?o=mr&page=%s", "Nofacegirl", "Pornhub: Nofacegirl"],
        ["/model/lis-evans/videos/upload?o=mr&page=%s", "Lis Evans", "Pornhub: Lis Evans"],
        ["/model/fantasybabe/videos/upload?o=mr&page=%s", "Fantasy Babe", "Pornhub: Fantasy Babe"],
        ["/model/mira-shark/videos/upload?o=mr&page=%s", "Mira Shark", "Pornhub: Mira Shark"],
        ["/model/luna-vitaler/videos/upload?o=mr&page=%s", "Luna Vitaler", "Pornhub: Luna Vitaler"],
        ["/pornstar/swife-katy/videos/upload?o=mr&page=%s", "SWife Katy", "Pornhub: SWife Katy"],
        ["/pornstar/tru-kait/videos/upload?o=mr&page=%s", "Tru Kait", "Pornhub: Tru Kait"],
        ["/model/comatozze/videos/upload?o=mr&page=%s", "Cumatozze", "Pornhub: Cumatozze"],
        ["/model/loly-nebel/videos/upload?o=mr&page=%s", "Loly Nebel", "Pornhub: Loly Nebel"],
        ["/model/teddy-tarantino/videos/upload?o=mr&page=%s", "Teddy Tarantino", "Pornhub: Teddy Tarantino"],
        ["/model/marycherry/videos/upload?o=mr&page=%s", "Mary Cherry", "Pornhub: MaryCherry"],
        ["/model/marybarrie/videos/upload?o=mr&page=%s", "Mary Cherry", "Pornhub: MaryBarrie"],
        ["/model/jean-summer/videos/upload?o=mr&page=%s", "Jean Summer", "Pornhub: Jean Summer"],
        ["/model/john-and-sky/videos/upload?o=mr&page=%s", "", "Pornhub: John and Sky"],
        ["/model/1twothreecum/videos/upload?o=mr&page=%s", "", "Pornhub: 1twothreecum"],
        ["/model/emilia-shot/videos/upload?o=mr&page=%s", "Emilia Shot", "Pornhub: Emilia Shot"],
        ["/model/lil-karina/videos/upload?o=mr&page=%s", "Lil Karina", "Pornhub: Lil Karina"],
        ["/model/lacyluxxx/videos?o=mr&page=%s", "Lacy Luxxx", "Pornhub: Lacy Luxxx"],
        ["/model/miss-ellie-moore/videos?o=mr&page=%s", "Miss Ellie Moore", "Pornhub: Miss Ellie Moore"],
        ["/model/guesswhox2/videos?o=mr&page=%s", "GuessWhoX2", "Pornhub: GuessWhoX2"],
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
