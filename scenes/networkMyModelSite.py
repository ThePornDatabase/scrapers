import re
from cleantext import clean
import string
from slugify import slugify
import scrapy
from requests import get
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMyModelSiteSpider(BaseSceneScraper):
    name = 'MyModelSite'

    studios = {
        "aeriefans.com": {
            "api": "aerie-saunders.mymember.site",
            "name": "Aerie Saunders",
        },
        "aglaeaproductions.com": {
            "api": "aglaeaproductions.mymember.site",
            "name": "Aglaea X",
        },
        "aliceshawbelly.com": {
            "api": "aliceshawbelly.mymember.site",
            "name": "Alice Shaw",
        },
        "allinthestepfamily.com": {
            "api": "all-in-the-step-family.mymember.site",
            "name": "All in the Step-Family"
        },
        "alterpic.com": {
            "api": "alterpic.mymember.site",
            "name": "Alterpic",
        },
        "amieesfetishhouse.com": {
            "api": "amiees-fetish-house.mymember.site",
            "name": "Amiees Fetish House",
        },
        "asianmassagemaster.com": {
            "api": "asianmassagemaster.mymember.site",
            "name": "Asian Massage Master",
        },
        "anistarxxx.com": {
            "api": "anistarxxx.mymember.site",
            "name": "AnniStar XXX",
        },
        "bdsmkinkyplay.com": {
            "api": "bdsmkinkyplay.mymember.site",
            "name": "BDSM Kinky Play",
        },
        "beverlybluexxx.com": {
            "api": "beverlybluexxx.mymember.site",
            "name": "BeverlyBlueXxX",
        },
        "bindastimesuk.com": {
            "api": "bindastimesuk.mymember.site",
            "name": "Bindastimesuk",
        },
        "bondageliberation.com": {
            "api": "bondageliberation.mymember.site",
            "name": "Bondage Liberation",
        },
        "brookesballoons.com": {
            "api": "brookesballoons.mymember.site",
            "name": "BrookesBalloons",
        },
        "castersworldwide.com": {
            "api": "castersworldwide.mymember.site",
            "name": "Casters Worldwide",
        },
        "chloestoybox.com": {
            "api": "chloestoybox.mymember.site",
            "name": "Chloe Toy",
        },
        "clubsteffi.fun": {
            "api": "clubsteffi.mymember.site",
            "name": "ClubSteffi",
        },
        "cristalkinky.com": {
            "api": "cristalkinky.mymember.site",
            "name": "Cristal Kinky",
        },
        "cruel-women.com": {
            "api": "cruel-women.mymember.site",
            "name": "Cruel Women",
        },
        "curvymary.com": {
            "api": "curvy-mary.mymember.site",
            "name": "Curvy Mary",
        },
        "dannijones.com": {
            "api": "dannijones.mymember.site",
            "name": "Danni Jones",
        },
        "deemariexxx.com": {
            "api": "deemariexxx.mymember.site",
            "name": "Dee Marie",
        },
        "europornvids.com": {
            "api": "europornvids.mymember.site",
            "name": "Euro Porn Vids",
        },
        "faexcheta.com": {
            "api": "faexcheta.mymember.site",
            "name": "Fae and Cheta",
        },
        "friskyfairyk.com": {
            "api": "friskyfairyk.mymember.site",
            "name": "xoXokmarie",
        },
        "girlsofhel.com": {
            "api": "girls-of-hel.mymember.site",
            "name": "Girls of HEL",
        },
        "glass-dp.com": {
            "api": "glassdp.mymember.site",
            "name": "Glassdp",
        },
        "glassdeskproductions.com": {
            "api": "glassdeskproductions.mymember.site",
            "name": "GlassDeskProductions",
        },
        "goddesslesley.com": {
            "api": "goddesslesley.mymember.site",
            "name": "Goddess Lesley",
        },
        "goddessrobin.com": {
            "api": "goddessrobin.mymember.site",
            "name": "Goddess Robin",
        },
        "greatbritishfeet.com": {
            "api": "greatbritishfeet.mymember.site",
            "name": "Great British Feet",
        },
        "greendoorlive.tv": {
            "api": "greendoorlivetv.mymember.site",
            "name": "The World Famous Green Door",
        },
        "heatheraustin.live": {
            "api": "heather-austin.mymember.site",
            "name": "Heather Austin",
        },
        "heavybondage4life.com": {
            "api": "heavybondage4life.mymember.site",
            "name": "Heavybondage4Life",
        },
        "hornyadventures.com": {
            "api": "hornyadventurestv.mymember.site",
            "name": "Horny Adventures",
        },
        "hornysilver.com": {
            "api": "hornysilver.mymember.site",
            "name": "Hornysilver",
        },
        "hotwifeheidihaze.com": {
            "api": "heidi-haze.mymember.site",
            "name": "Heidi Haze",
        },
        "islandboyvids.com": {
            "api": "islandboyvids.mymember.site",
            "name": "Island Boy Vids",
        },
        "josyblack.tv": {
            "api": "josyblack.mymember.site",
            "name": "Josy Black",
        },
        "juteandroses.com": {
            "api": "juteandroses.mymember.site",
            "name": "Jute and Roses",
        },
        "kingnoirexxx.com": {
            "api": "kingnoirexxx.mymember.site",
            "name": "KingNoireXXX",
        },
        "kinkography.com": {
            "api": "kinkography.mymember.site",
            "name": "Kinkography",
        },
        "kinkyponygirl.com": {
            "api": "kinkyponygirl.mymember.site",
            "name": "KinkyPonygirl",
        },
        "kinkyrubberdreams.com": {
            "api": "kinkyrubberdreams.mymember.site",
            "name": "Glowing Darkness",
        },
        "kitehkawasaki.com": {
            "api": "kitehkawasaki.mymember.site",
            "name": "Kiteh Kawasaki",
        },
        "labelladx.com": {
            "api": "labelladx.mymember.site",
            "name": "LaBellaDiablaX",
        },
        "lady-asmondena.com": {
            "api": "ladyasmondena.mymember.site",
            "name": "Lady Asmondena",
        },
        "lamodelsdoporn.com": {
            "api": "lamodelsdoporn.mymember.site",
            "name": "LA Models Do Porn",
        },
        "latexkittyxxx.com": {
            "api": "latexkittyxxx.mymember.site",
            "name": "Latexkittyxxx",
        },
        "latexlolanoir.com": {
            "api": "latexlolanoir.mymember.site",
            "name": "Lola Noir",
        },
        "latexrapturefans.com": {
            "api": "latexrapturefans.mymember.site",
            "name": "LatexRapture",
        },
        "letseatcakexx.com": {
            "api": "letseatcakexx.mymember.site",
            "name": "Lets Eat Cake",
        },
        "loonerlanding.com": {
            "api": "loonerlanding.mymember.site",
            "name": "Looner Landing",
        },
        "lukespov.vip": {
            "api": "lukespov.mymember.site",
            "name": "Luke's POV",
        },
        "marvalstudio.com": {
            "api": "marvalstudio.mymember.site",
            "name": "MarValStudio",
        },
        "michaelfittnation.com": {
            "api": "michaelfittnation.mymember.site",
            "name": "Michael Fitt",
        },
        "milenaangel.club": {
            "api": "milenaangel.mymember.site",
            "name": "MilenaAngel",
        },
        "mondofetiche.com": {
            "api": "mondofetiche.mymember.site",
            "name": "Mondo Fetiche",
        },
        "mrhappyendings.com": {
            "api": "mrhappyendings.mymember.site",
            "name": "Mr Happy Endings",
        },
        "mymember.site/Goddessjazzy": {
            "api": "goddessjazzy.mymember.site",
            "name": "Goddess Jazzy",
        },
        "mymember.site/androprince-cs-chamber/": {
            "api": "androprince-cs-chamber.mymember.site",
            "name": "AndroPrince C's Chamber",
        },
        "mymember.site/aoikamogawa": {
            "api": "aoikamogawa.mymember.site",
            "name": "Aoi Kamogawa",
        },
        "mymember.site/eroticious": {
            "api": "eroticious.mymember.site",
            "name": "eroticious",
        },
        "mymember.site/kyara-in-ropes": {
            "api": "kyara-in-ropes.mymember.site",
            "name": "Kyara in Ropes",
        },
        "mymember.site/latex-desire": {
            "api": "latex-desire.mymember.site",
            "name": "LatexDesire",
        },
        "mymember.site/linaroselina": {
            "api": "linaroselina.mymember.site",
            "name": "Lina Roselina",
        },
        "mymember.site/mr-rains-sexy-wrestling": {
            "api": "mr-rains-sexy-wrestling.mymember.site",
            "name": "Mr Rains Sexy Wrestling",
        },
        "mymember.site/officialemyang": {
            "api": "officialemyang.mymember.site",
            "name": "Official Em Yang",
        },
        "mymember.site/rubbobjectdoll": {
            "api": "rubbobjectdoll.mymember.site",
            "name": "RubbobjectDoll",
        },
        "nicoledupapillon.net": {
            "api": "nicole-dupapillon.mymember.site",
            "name": "Nicole DuPapillon",
        },
        "nikitzo.com": {
            "api": "nikitzo.mymember.site",
            "name": "NIKITZO",
        },
        "nikkidavisxo.com": {
            "api": "nikkidavisxo.mymember.site",
            "name": "NikkiDavisXO",
        },
        "nylon-encasement.com": {
            "api": "nylon-encasement.mymember.site",
            "name": "Nylon Encasement",
        },
        "peacockcouple.com": {
            "api": "peacockcouple.mymember.site",
            "name": "PeacockCouple",
        },
        "pedal-passion.com": {
            "api": "pedal-passion.mymember.site",
            "name": "Pedal Passion",
        },
        "pervfect.net": {
            "api": "pervfect.mymember.site",
            "name": "Pervfect",
        },
        "psilosirenxxx.com": {
            "api": "psilosirenxxx.mymember.site",
            "name": "PsiloSiren",
        },
        "riggsfilms.vip": {
            "api": "riggsfilms.mymember.site",
            "name": "Riggs Films",
        },
        "royalfetishxxx.com": {
            "api": "royalfetishxxx.mymember.site",
            "name": "RoyalFetishXXX",
        },
        "rubber-pervs.com": {
            "api": "rubberpervs.mymember.site",
            "name": "Rubber-Pervs",
        },
        "rubberdollemmalee.com": {
            "api": "rubberdollemmalee.mymember.site",
            "name": "Rubberdoll Emma Lee",
        },
        "sam-serenity.com": {
            "api": "sam-serenity.mymember.site",
            "name": "Sam Serenity",
        },
        "sexyhippies.com": {
            "api": "sexyhippies.mymember.site",
            "name": "Sexy Hippies",
        },
        "shemalevalentina.com": {
            "api": "shemalevalentina.mymember.site",
            "name": "Shemale Valentina",
        },
        "slutwife.club": {
            "api": "slutwife-club.mymember.site",
            "name": "SLUTWIFE CLUB",
        },
        "spanishxbarbiiexxx.com": {
            "api": "spanishxbarbiie.mymember.site",
            "name": "Spanish Barbie",
        },
        "strong-men.com": {
            "api": "strong-men.mymember.site",
            "name": "Strong-Men",
        },
        "tabooseduction.com": {
            "api": "tabooseduction.mymember.site",
            "name": "TabooSeduction",
        },
        "taboosexstories4k.com": {
            "api": "taboosexstories4k.mymember.site",
            "name": "Taboo Sex Stories",
        },
        "the-strapon-site.com": {
            "api": "thestraponsite.mymember.site",
            "name": "The Strapon Site",
        },
        "theextortionarium.com": {
            "api": "the-extortionarium.mymember.site",
            "name": "The Extortionarium",
        },
        "thegoonhole.com": {
            "api": "thegoonhole.mymember.site",
            "name": "The Goonhole",
        },
        "thekandikjewel.com": {
            "api": "thekandikjewel.mymember.site",
            "name": "The Kandi K Jewel",
        },
        "unlimited.lovely-anita.com": {
            "api": "lovelyanita.mymember.site",
            "name": "Lovely Anita",
        },
        "whatlizannelikes.com": {
            "api": "whatlizannelikes.mymember.site",
            "name": "What Lizanne Likes",
        },
        "yourfitcrush.com": {
            "api": "yourfitcrush.mymember.site",
            "name": "Your Fit Crush",
        },
    }

    selector_map = {
        'external_id': r'',
        'pagination': '/api/videos?count=20&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for studio in self.studios:
            meta['studio_url'] = studio
            meta['api_url'] = "https://" + self.studios[studio]['api']
            meta['site'] = self.studios[studio]['name']
            yield scrapy.Request(url=self.get_next_page_url(meta['api_url'], self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['data']
        for scene in jsondata:
            meta['id'] = scene['id']
            meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publish_date']).group(1)
            meta['title'] = string.capwords(scene['title'])
            meta['duration'] = str(scene['duration'])
            scene_url = f"{meta['api_url']}/api/videos/{meta['id']}"
            yield scrapy.Request(scene_url, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()
        scene = response.json()

        item['title'] = meta['title']
        item['date'] = meta['date']
        item['id'] = meta['id']
        item['duration'] = meta['duration']

        if scene['description']:
            description = clean(scene['description'].replace("\n", "").strip(), no_emoji=True)
            item['description'] = self.cleanup_description(description)

        if "poster_src" in scene and scene['poster_src']:
            item['image'] = scene['poster_src']
            if 'image' not in item or not item['image']:
                item['image'] = None
                item['image_blob'] = None
            else:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if 'image_blob' not in item:
                item['image'] = None
                item['image_blob'] = None

            if item['image']:
                if "?" in item['image']:
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['tags'] = []
        if "tags" in scene and scene['tags']:
            for tag in scene['tags']:
                item['tags'].append(tag['name'])

        if "casts" in scene and scene['casts']:
            item['performers'] = []
            for cast in scene['casts']:
                item['performers'].append(cast['screen_name'])

            # ~ item['performers_data'] = self.get_performers_data(item['performers'], meta['site'])

        item['url'] = f"https://{meta['studio_url']}/videos/{item['id']}-{slugify(item['title'])}"

        item['site'] = meta['site']
        item['parent'] = meta['site']
        item['network'] = meta['site']

        item['type'] = 'Scene'

        yield self.check_item(item, self.days)

    def get_performers_data(self, performers, site):
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = site
                perf['site'] = site
                performers_data.append(perf)
        return performers_data
