"""
Scraper for ManyVids network.
If adding sites, please use the 'Manyvids: <site/performername>' format
This helps keep them together on the site without mixing in what are
usually more or less camgirls into the regular sites
"""
import re
import html
import json
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkManyVidsV2Spider(BaseSceneScraper):
    name = 'ManyVidsV2'

    start_urls = [
        ['1001216419', 'YouthLust', False],
        ['214657', 'Manyvids: Lana Rain', True],
        ['423053', 'MySweetApple', False],
        ['1001495638', 'Manyvids: Jack and Jill', False],
        ['325962', 'Manyvids: Dirty Princess', False],
        ['312711', 'Manyvids: Cattie', False],
        ['1000286888', 'A Taboo Fantasy', False],
        ['694469', 'Adult Candy Store', False],
        ['1000159044', 'Fuck Club', False],
        ['1000380769', 'IXXVICOM', False],
        ['806007', 'Jay Bank Presents', False],
        ['1001483477', 'Undercover Sluts', False],
        # ~ # ['574529', 'Submissive Teen POV, False'],  # Seems to have gone away, leaving for reference
        ['1002638751', 'Sloppy Toppy', False],
        ['69353', 'Natalia Grey', False],
        ['97815', 'Manyvids: Hidori', True],
        ['1001123043', 'Manyvids: Paige Steele', True],
        ['1001317123', 'Manyvids: Jaybbgirl', True],
        ['1001673578', 'Manyvids: FreyaJade', False],
        ['304591', 'Manyvids: 420SexTime', False],
        ['217682', 'Manyvids: OmankoVivi', False],
        ['1000304351', 'Manyvids: Haylee Love', True],
        ['1002322838', 'Manyvids: Jewelz Blu', True],
        ['1003298627', 'Manyvids: Molly Redwolf', True],
        ['1003004427', 'Manyvids: Sweetie Fox', True],
        ['32539', 'Manyvids: Cherry Crush', True],
        ['35990', 'Manyvids: Charlette Webb', True],
        ['91512', 'Manyvids: Alli Leigh', True],
        ['65933', 'Manyvids: Little Miss Elle', True],
        ['216064', 'Manyvids: Lena Spanks', True],
        ['251896', 'Manyvids: Submissive Lexi', True],
        ['1004407943', 'Manyvids: Sloansmoans', False],
        ['491714', 'Manyvids: ImMeganLive', True],
        ['577443', 'Manyvids: Emmas Secret Life', False],
        ['375403', 'Manyvids: Natashas Bedroom', False],
        ['102036', 'Manyvids: Ashley Alban', True],
        ['147843', 'Manyvids: Penny Barber', True],
        ['38793', 'Manyvids: Princess Leia', True],
        ['1003527333', 'Manyvids: Kathia Nobili', True],
        ['1004207044', 'Manyvids: Mrs Mischief', True],
        ['1000997612', 'Manyvids: MistressT', True],
        ['1005123610', 'Manyvids: Tara Tainton', True],
        ['1001836304', 'Manyvids: Siena Rose', True],
        ['273124', 'Manyvids: Courtney Scott', True],
        ['1000856699', 'Manyvids: Kiittenymph', False],
        ['1004388117', 'Manyvids: ForbiddenFruitsFilms', False],
        ['1004388132', 'Manyvids: Jodi West', True],
        ['320527', 'Manyvids: Diane Andrews', True],
        ['1000324638', 'Manyvids: Blissed XXX', False],
        ['1004131603', 'Manyvids: Chris And Mari', False],
        ['1000829435', 'Manyvids: RhiannonRyder1995', False],
        ['1001194277', 'Manyvids: Legendarylootz', True],
        ['1002393375', 'Manyvids: Natasha Nixx', True],
        ['208703', 'Manyvids: Tatum Christine', True],
        ['150576', 'Manyvids: xxxCaligulaxxx', True],
        ['1004057036', 'Manyvids: Amber Hallibell', True],
        ['1000691111', 'Manyvids: Purple Bitch', True],
        ['1003667583', 'Manyvids: Im Heather Harmon', False],
        ['590705', 'Manyvids: Bettie Bondage', True],
        ['1002042328', 'Manyvids: Jade Vow', True],
        ['518153', 'Manyvids: Naughty Midwest Girls', False],
        ['1002715079', 'Manyvids: Alice Bong', True],
        ['1002319155', 'Manyvids: Sola Zola', True],
        ['1002133241', 'Manyvids: Reislin', True],
        ['1000107977', 'Manyvids: Chad Alva', True],
        ['1000228944', 'Manyvids: Heather Vahn', True],
        ['1002812736', 'Manyvids: Tommy Wood', True],
        ['1000657719', 'Manyvids: Dawns Place', False],
        ['1004225528', 'Manyvids: MyLittleSwallow', False],
        ['1000933793', 'Manyvids: Sukisukigirl', True],
        ['1005546662', 'Manyvids: Andregotbars', True],
        ['1003828607', 'Manyvids: Brandibabes', False],
        ['602138', 'Manyvids: WCA Productions', False],
        ['1002621197', 'Manyvids: Riley Jacobs', True],
        ['1001106526', 'Manyvids: Lola Rose', True],
        ['1002865441', 'Manyvids: Luna Roulette', True],
        ['1003906145', 'Manyvids: Octokuro', True],
        ['1004893370', 'Manyvids: TheGorillaGrip', True],
        ['1004855103', 'Manyvids: Angelphub', True],
        ['1002214325', 'Manyvids: Senorita Satan', False],
        ['1002980475', 'Manyvids: Peachy Skye', True],
        ['1003834874', 'Manyvids: Summer Fox', True],
        ['1002023399', 'Manyvids: Daddys Rozay', True],
        ['1000452244', 'Manyvids: Ondrea Lee', True],
        ['1000862654', 'Manyvids: Horny Lily', True],
        ['1000182655', 'Manyvids: Nicole Belle', True],
        ['419692', 'Manyvids: Little Puck', True],
        ['1002190635', 'Manyvids: Violet Myers', True],
        ['65682', 'Manyvids: Krissy Lynn', True],
        ['1001368680', 'Manyvids: Smiles of Sally', False],
        ['1001768929', 'Manyvids: Natalie Wonder', True],
        ['522512', 'Manyvids: Sally Dangelo', True],
        ['54610', 'Manyvids: Lanie Love', True],
        ['1000534648', 'Manyvids: Jenni Knight', True],
        ['1000833600', 'Manyvids: Miss Ellie', True],
        ['1003962281', 'Manyvids: Little Bunny B', True],
        ['1000675514', 'Manyvids: The Queen Lanie', True],
        ['1003387859', 'Manyvids: Britney Amber', True],
        ['1002555505', 'Manyvids: Taboo Saga', False],
        ['1001830287', 'Manyvids: Lani Lust', True],
        ['549738', 'Manyvids: Lissie Belle', True],
        ['1004243978', 'Manyvids: Pepperanncan', False],
        ['1001213004', 'Manyvids: Sydney Harwin', True],
        ['115565', 'Manyvids: ohaiNaomi', True],
        ['1005854378', 'Manyvids: Trisha Moon', True],
        ['1003987502', 'Manyvids: 2 Drops Studio', False],
        ['49000', 'Manyvids: BuniBun', True],
        ['620931', 'Manyvids: Mylene', True],
        ['1002463312', 'Manyvids: Oralsonly', False],
        ['1002067521', 'Manyvids: Zirael Rem', True],
        ['1000764908', 'Manyvids: Tweetney', True],
        ['1004557133', 'Manyvids: Aery Tiefling', True],
        ['1000945715', 'Manyvids: Alexa Pearl', True],
        ['1003572193', 'Manyvids: Vina Sky', True],
        ['525062', 'Manyvids: JaySmoothXXX', False],
        ['1001301396', 'Manyvids: Sia Siberia', True],
        ['358347', 'Manyvids: LittleSubGirl', True],
        ['106308', 'Manyvids: OUSweetheart', False],
        ['1003025690', 'Manyvids: Laura King', True],
        ['1004485402', 'Manyvids: TheSophieJames', False],
        ['456897', 'Manyvids: Fell On Productions', False],
        ['362540', 'Manyvids: Ivy Starshine', True],
        ['1000718761', 'Manyvids: Jane Cane', True],
        ['1001244409', 'Manyvids: Yogabella', True],
        ['1002612831', 'Manyvids: Mama Fiona', True],
        ['1004271325', 'Manyvids: Peachypoppy', True],
        ['1000297683', 'Manyvids: Marica Hase', True],
        ['1004225528', 'Manyvids: MyLittleSwallow', True],
        ['167615', 'Manyvids: Reagan Foxx', True],
        ['541454', 'Manyvids: Lena Paul', True],
        ['1004357188', 'Manyvids: AimeeWavesXXX', True],
        ['1004323423', 'Manyvids: Bella Bates', True],
        ['1007113302', 'Manyvids: Funsizedcumslut', True],
        ['30313', 'Manyvids: Alix Lynx', True],
        ['1000567799', 'Manyvids: Made In Canarias', True],
        ['826394', 'Manyvids: Lexxxi Luxe', True],
        ['1004385584', 'Manyvids: Slut Me Out Now', False],
        ['1000024307', 'Manyvids: Brea Rose', True],
        ['375644', 'Manyvids: Delphoxi', True],
        ['1000457016', 'Manyvids: EastCoastXXX', False],
        ['1002460913', 'Manyvids: Leah Meow', True],
        ['1003179211', 'Manyvids: Phatassedangel69', True],
        ['1002698505', 'Manyvids: Nicole Doshi', True],
        ['1002219117', 'Manyvids: Gogofukmexxx', False],
        ['1003672212', 'Manyvids: Sonya Vibe', True],
        ['380172', 'Manyvids: Raquel Roper', True],
        ['1003468856', 'Manyvids: Vitaduplez', True],
        ['1005161332', 'Manyvids: Lauryn Mae', True],
        ['353960', 'Manyvids: Arabelle Raphael', True],
        ['1003125256', 'Manyvids: Halfwin', True],
        ['1004334654', 'Manyvids: ASMRMaddy', True],
        ['1000722201', 'Manyvids: Jada Kai', True],
        ['1001389615', 'Manyvids: Kimberlyjx', True],
        ['1003079493', 'Manyvids: Luke Cooper', True],
        ['673872', 'Manyvids: Veruca James', True],
        ['34', 'Manyvids: Angie Noir', True],
        ['528941', 'Manyvids: Rae Knight', True],
        ['1001803967', 'Manyvids: xxxmultimediacom', False],
        ['152830', 'Manyvids: Anna Bell Peaks', True],
        ['539280', 'Manyvids: Kimberly Kane', True],
        ['1001516727', 'Manyvids: Vanessa Veracruz', True],
        ['599647', 'Manyvids: Forbidden Perversions', False],
        ['1002202911', 'Manyvids: Hazel Simone', True],
        ['1002587264', 'Manyvids: Golden Lace', True],
        ['1005049819', 'Manyvids: Lewdest Bunnie', True],
        ['83782', 'Manyvids: oopepperoo', True],
        ['124871', 'Manyvids: Olive Wood', True],
        ['1000532441', 'Manyvids: Rhea Sweet', True],
        ['159708', 'Manyvids: Robin Mae', True],
        ['1005790100', 'Manyvids: Sugary_Kitty', True],
        ['1005503479', 'Manyvids: ThaiNymph', True],
        ['1001576946', 'Manyvids: InkedMonster', True],
        ['1007502059', 'Manyvids: ThaiGyaru', True],
        ['1006075221', 'Manyvids: ThaiSprite', True],
        ['1002249501', 'Manyvids: KCupQueen', True],
        ['1000468027', 'Manyvids: Evie Rees', True],
        ['1001996011', 'Manyvids: lalunalewd', True],
        ['1003079099', 'Manyvids: Lia Lennice', True],
        ['1005093292', 'Manyvids: IndiscreetHotAndFit', True],
        ['1002200110', 'Manyvids: LaceyinLaLaLand', False],
        ['345718', 'Manyvids: Mona Wales', True],
        ['1000053441', 'Manyvids: Julie Snow', True],
        ['830429', 'Manyvids: Gala MV', True],
        ['1002818112', 'Manyvids: Nicole Nabors', True],
        ['494106', 'Manyvids: AuroraXoxo', True],
        ['1001211849', 'Manyvids: Ksu Colt', True],
        ['1004472635', 'Manyvids: Sybil Raw', True],
        ['1005948542', 'BJ World', False],
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False'}

    selector_map = {
        'title': '',
        'description': '//div[contains(@class, "desc-text")]/text()',
        'date': '//div[@class="mb-1"]/span[1]/span[2]|//div[@class="mb-1"]/span[2]/text()',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '',
        'tags': '//script[contains(text(),"tagListApp")]/text()',
        'duration': '//div[@class="video-details"]//i[contains(@class, "mv-icon-video-length")]/following-sibling::text()[contains(., "min")]',
        're_duration': r'(\d{1,2}\:.*?) min',
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }

    def start_requests(self):
        url = "https://www.manyvids.com/Profile/1001216419/YouthLust/Store/Videos/"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        meta = response.meta
        meta['mvtoken'] = response.xpath('//html/@data-mvtoken').get()
        self.headers['referer'] = 'https://www.manyvids.com/Profile/1003004427/Sweetie-Fox/Store/Videos/'

        for link in self.start_urls:
            meta['page'] = self.page
            meta['siteid'] = link[0]
            meta['site'] = link[1]
            meta['parse_performer'] = link[2]
            yield scrapy.Request(url=self.get_next_page_url(self.page, meta), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response):
        # ~ print(response.text)
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, page, meta):
        offset = str((int(page) - 1) * 30)
        link = f"https://www.manyvids.com/api/model/{meta['siteid']}/videos?category=all&offset={offset}&sort=0&limit=30&mvtoken={meta['mvtoken']}"
        return link

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        data = jsondata['result']['content']['items']
        for jsonentry in data:
            meta['id'] = jsonentry['id']
            meta['title'] = string.capwords(html.unescape(jsonentry['title']))
            scenelink = f"https://video-player-bff.estore.kiwi.manyvids.com/videos/{meta['id']}"
            if meta['id']:
                yield scrapy.Request(scenelink, callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        meta = response.meta
        if meta['parse_performer']:
            performer = re.search(r'Manyvids:(.*)$', meta['site']).group(1).strip()
            return [performer]
        else:
            if meta['site'] == "Cattie":
                return ['Cattie Candescent']
            if "Brandibabes" in meta['site']:
                return ['Brandi Babes']
            if "Gogofukmexxx" in meta['site']:
                return ['Gogo Fukme']
            if "FreyaJade" in meta['site']:
                return ['Freya Jade']
            if "420SexTime" in meta['site']:
                return ['Asteria']
            if "OmankoVivi" in meta['site']:
                return ['Omanko Vivi']
            if "RhiannonRyder1995" in meta['site']:
                return ['Rhiannon Ryder']
            if "Kiittenymph" in meta['site']:
                return ['Lex Kiittenymph']
            if "ForbiddenFruitsFilms" in meta['site']:
                return ['Jodi West']
            if "OUSweetheart" in meta['site']:
                return ['Summer Hart']
            if "Senorita Satan" in meta['site']:
                return ['Chloe Temple']
            if "TheSophieJames" in meta['site']:
                return ['Sophie James']
        return []

    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return "Manyvids"

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            if "Manyvids" in meta['site']:
                return "Manyvids"
            return meta['site']
        return "Manyvids"

    def get_network(self, response):
        return "Manyvids"

    def parse_scene(self, response):
        item = SceneItem()
        meta = response.meta
        jsondata = json.loads(response.text)
        item['title'] = meta['title']
        item['id'] = meta['id']
        if 'description' in jsondata:
            item['description'] = jsondata['description']
        else:
            item['description'] = ""
        if "tags" in jsondata:
            item['tags'] = jsondata['tags']
        else:
            item['tags'] = []
        item['image'] = jsondata['screenshot'].replace(" ", "%20")
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['image'] = re.sub(r'(.*)(\.\w{3,4})$',r'\1_1\2', item['image'])
        item['date'] = jsondata['launchDate']
        item['trailer'] = None
        item['type'] = 'Scene'
        item['network'] = "Manyvids"
        item['performers'] = self.get_performers(response)
        item['site'] = self.get_site(response)
        item['parent'] = self.get_parent(response)
        item['url'] = "https://www.manyvids.com" + jsondata['url']
        if "videoDuration" in jsondata:
            duration = re.search(r'(\d{1,2}:\d{1,2}:?\d{1,2}?)', jsondata['videoDuration'])
            item['duration'] = self.duration_to_seconds(duration.group(1))
        else:
            item['duration'] = ""
        parse_scene = True
        if "eastcoastxxx" in item['site'].lower():
            matches = ['-free', '-tube', 'free-preview', 'free preview', '-teaser']
            if any(x in item['url'].lower() for x in matches):
                parse_scene = False
        if parse_scene:
            yield self.check_item(item, self.days)
