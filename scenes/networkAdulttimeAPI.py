import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

# NOTE!   This scraper _ONLY_ pulls scenes from AdultTime sites with publicly available video index pages.
#         It will not pull any scenes or images that are unavailable if you simply go to the specific site
#         as a guest user in an incognito browser


def match_site(argument):
    match = {
        '21eroticanal': '21 Erotic Anal',
        '21footart': '21 Foot Art',
        '21naturals': '21Naturals',
        '21sextury': '21Sextury',
        '21sextreme': '21Sextreme',
        '3rddegreefilms': '3rd Degree Films',
        'activeduty': 'Active Duty',
        'adamandevepictures': 'Adam and Eve Pictures',
        'addicted2girls': 'Addicted2Girls',
        'adulttime': 'AdultTime',
        'agentredgirl': 'Agent Red Girl',
        'ageandbeauty': 'Age and Beauty',
        'alettaoceanempire': 'Aletta Ocean Empire',
        'allgirlmassage': 'All Girl Massage',
        'analqueenalysa': 'Anal Queen Alysa',
        'analteenangels': 'Anal Teen Angels',
        'asmr-fantasy': 'ASMR Fantasy',
        'asmrfantasy': 'ASMR Fantasy',
        'assholefever': 'Asshole Fever',
        'austinwilde': 'Austin Wilde',
        'babygotballs': 'Baby Got Balls',
        'biphoria': 'BiPhoria',
        'bethecuck': 'Be The Cuck',
        'blacksonblondes': 'Blacks on Blondes',
        'blueangellive': 'Blue Angel Live',
        'burningangel': 'Burning Angel',
        'buttplays': 'Buttplays',
        'chaosmen': 'Chaos Men',
        'cheatingwhorewives': 'Cheating Whore Wives',
        'clubinfernodungeon': 'Club Inferno Dungeon',
        'clubsandy': 'Club Sandy',
        'codycummings': 'Cody Cummings',
        'couple-swapping': 'Couple Swapping',
        'coupleswapping': 'Couple Swapping',
        'creampiereality': 'Creampie Reality',
        'cummingmatures': 'Cumming Matures',
        'cutiesgalore': 'Cuties Galore',
        'deepthroatfrenzy': 'Deepthroat Frenzy',
        'diabolic': 'Diabolic',
        'devilsfilm': 'Devils Film',
        'devilsfilmparodies': 'Devils Film Parodies',
        'devilsgangbangs': 'Devils Gangbangs',
        'devilstgirls': 'Devils T-Girls',
        'dominatedgirls': 'Dominated Girls',
        'downlowboys': 'Downlow Boys',
        # 'dpfanatics': 'DPFanatics', Pulled from Gamma
        'evilangel': 'Evil Angel',
        'falconstudios': 'Falcon Studios',
        'fantasymassage': 'Fantasy Massage',
        'femalesubmission': 'Female Submission',
        'femboyish': 'Femboyish',
        'footsiebabes': 'Footsie Babes',
        'gangbangcreampie': 'Gangbang Creampie',
        'gapeland': 'Gapeland',
        'genderx': 'Gender X',
        'genderxfilms': 'Gender X',
        'girlcore': 'Girlcore',
        'girlsunderarrest': 'Girls Under Arrest',
        'girlstryanal': 'Girls Try Anal',
        'girlsway': 'Girlsway',
        'givemeteens': 'Give Me Teens',
        'gloryholesecrets': 'Gloryhole Secrets',
        'grandpasfuckteens': 'Grandpas Fuck Teens',
        'hairyundies': 'Hairy Undies',
        'homepornreality': 'Home Porn Reality',
        'hotmilfclub': 'Hot MILF Club',
        'interracialvision': 'Interracialvision',
        'isthisreal': 'Is This Real',
        'JaneDoePictures': 'Jane Doe Pictures',
        'joymii': 'JoyMii',
        'kissmefuckme': 'Kiss Me Fuck Me',
        'ladygonzo': 'Lady Gonzo',
        'lesbianfactor': 'Lesbian Factor',
        'letsplaylez': 'Lets Play Lez',
        'lewood': "Lewood",
        'lez-be-bad': 'Lez Be Bad',
        'lezcuties': 'Lez Cuties',
        'lustygrandmas': 'Lusty Grandmas',
        'mandyiskinky': 'Mandy Is Kinky',
        'marcusmojo': 'Marcus Mojo',
        'masonwyler': 'Mason Wyler',
        'massageparlor': 'Massage Parlor',
        'mightymistress': 'Mighty Mistress',
        'mixedx': 'Mixed X',
        'modeltime': 'Model Time',
        'moderndaysins': 'Modern Day Sins',
        'mommysgirl': 'Mommys Girl',
        'momsonmoms': 'Moms on Moms',
        'mypervyfamily': 'My Pervy Family',
        'nakedyogalife': 'Naked Yoga Life',
        'nextdoorbuddies': 'Nextdoor Buddies',
        'nextdoorcasting': 'Nextdoor Casting',
        'nextdoorhomemade': 'Nextdoor Homemade',
        'nextdoorhookups': 'Nextdoor Hookups',
        'nextdoormale': 'Nextdoor Male',
        'nextdoororiginals': 'Nextdoor Originals',
        'nextdoorraw': 'Nextdoor Raw',
        'nextdoorstudios': 'Nextdoor Studios',
        'nextdoortwink': 'Nextdoor Twink',
        # 'nudefightclub': 'Nude Fight Club', Pulled from Gamma
        'nurumassage': 'Nuru Massage',
        'oldyounglesbianlove': 'Old Young Lesbian Love',
        'oralexperiment': 'Oral Experiment',
        'outofthefamily': 'Out of the Family',
        'peeandblow': 'Pee And Blow',
        'pixandvideo': 'Pix And Video',
        'povthis': "POV This",
        'prettydirty': "Pretty Dirty",
        'puretaboo': 'Pure Taboo',
        'ragingstallion': 'Raging Stallion Studios',
        'roccosiffredi': 'Rocco Siffredi',
        'roddaily': 'Rod Daily',
        'samuelotoole': 'Samuel Otoole',
        'sistertrick': 'Sister Trick',
        'sextapelesbians': 'Sextape Lesbians',
        'sexwithkathianobili': 'Sex With Kathia Nobili',
        'soapymassage': 'Soapy Massage',
        'showersolos': 'Shower Solos',
        'speculumplays': 'Speculum Plays',
        'squirtalicious': 'Squirtalicious',
        'stagcollectivesolos': 'Stag Collective Solos',
        'strokethatdick': 'Stroke That Dick',
        'sweetsophiemoone': 'Sweet Sophie Moon',
        'tabooheat': 'Taboo Heat',
        'teachmefisting': 'Teach Me Fisting',
        'teensneaks': 'Teen Sneaks',
        'thebrats': 'The Brats',
        'themikeandjoannashow': 'The Mike and Joanna Show',
        'tommydxxx': 'Tommy D XXX',
        'touchmywife': 'Touch My Wife',
        'transfixed': 'Transfixed',
        'trickyspa': 'Tricky Spa',
        'transfrombrazil': 'Trans From Brazil',
        'TransgressiveFilms': 'Transgressive Films',
        'transsexualroadtrip': "Transsexual Roadtrip",
        'transsmuts': 'Trans Smuts',
        'truelesbian.com': 'True Lesbian',
        'trystanbull': 'Trystan Bull',
        'tsfactor': 'TS Factor',
        'webyoung': 'Web Young',
        'welikegirls': 'We Like Girls',
        'wheretheboysarent': 'Where the Boys Arent',
        'wicked': 'Wicked',
        'zerotolerancefilms': 'Zero Tolerance',
        'zoliboy': 'Zoliboy',
    }
    return match.get(argument.lower(), argument)


class AdultTimeAPISpider(BaseSceneScraper):
    name = 'AdulttimeAPI'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://www.agentredgirl.com',
        'https://www.21naturals.com',
        'https://www.21sextreme.com',
        'https://www.21sextury.com',
        'https://www.activeduty.com',
        'https://www.addicted2girls.com',
        'https://www.adulttime.com/series/asmr-fantasy',
        'https://www.adulttime.com/series/couple-swapping',
        'https://www.adulttime.com/series/kiss-me-fuck-me',
        'https://www.adulttime.com/series/lez-be-bad',
        'https://www.adulttime.com/series/naked-yoga-life',
        'https://www.adulttime.com/series/oopsie',
        'https://www.adulttime.com/series/she-wants-him',
        'https://www.adulttime.com/series/shower-solos',
        'https://www.adulttime.com/series/switch',
        'https://www.adulttime.com/series/teen-sneaks',
        'https://www.adulttime.com/series/the-mike-and-joanna-show',
        'https://www.adulttime.com/series/with-love-lexi',
        'https://www.adulttime.com/studio/adam-and-eve-pictures',
        'https://www.ageandbeauty.com',
        'https://www.allblackx.com',
        'https://www.biphoria.com',
        'https://www.blowpass.com',
        'https://www.chaosmen.com',
        'https://www.clubinfernodungeon.com',
        'https://www.darkx.com',
        'https://www.devilsfilm.com',
        'https://www.diabolic.com',
        'https://www.dfxtra.com',
        'https://www.downlowboys.com',
        'https://www.dpfanatics.com',
        'https://www.eroticax.com',
        'https://www.evilangel.com',
        'https://www.falconstudios.com',
        'https://www.famedigital.com',
        'https://www.fantasymassage.com',
        'https://www.femboyish.com',
        'https://www.filthykings.com',
        'https://www.footsiebabes.com',
        'https://www.gangbangcreampie.com',
        # 'https://www.genderx.com', Now GenderXFilms
        'https://www.genderxfilms.com',
        'https://www.girlfriendsfilms.com',
        'https://www.girlsway.com',
        'https://www.gloryholesecrets.com',
        'https://www.hardx.com',
        'https://www.interracialvision.com',
        'https://www.isthisreal.com',
        'https://www.jerk-buddies.com',
        'https://www.joymii.com',
        'https://www.ladygonzo.com',
        'https://www.lesbianx.com',
        'https://www.lethalhardcore.com',
        'https://www.lethalhardcorevr.com',
        'https://www.lewood.com',
        'https://www.mixedx.com',
        'https://www.modeltime.com',
        'https://www.moderndaysins.com',
        'https://www.mommysgirl.com',
        'https://www.mypervyfamily.com',
        'https://www.nextdoorstudios.com',
        'https://www.peternorth.com',
        'https://www.povthis.com',
        'https://www.prettydirty.com',
        'https://www.pridestudios.com',
        'https://www.puretaboo.com',
        'https://www.ragingstallion.com',
        'https://www.roccosiffredi.com',
        'https://www.shapeofbeauty.com',
        'https://www.tabooheat.com',
        'https://www.thebrats.com',
        'https://www.touchmywife.com',
        'https://www.transfixed.com',
        'https://www.transsexualroadtrip.com',
        'https://www.truelesbian.com',
        'https://www.tsfactor.com',
        'https://tour1.vivid.com',
        'https://www.wicked.com',
        'https://www.xempire.com',
        'https://www.zerotolerancefilms.com',
    ]

    image_sizes = [
        '1920x1080',
        '1280x720',
        '960x544',
        '638x360',
        '201x147',
        '406x296',
        '307x224'
    ]

    trailer_sizes = [
        '1080p',
        '720p',
        '4k',
        '540p',
        '480p',
        '360p',
        '240p',
        '160p'
    ]

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'CONCURRENT_REQUESTS': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'CONCURRENT_REQUESTS_PER_IP': 4,
        "MEDIA_ALLOW_REDIRECTS": True,
    }

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/en/videos?page=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')
        page = int(self.page) - 1

        for link in self.start_urls:
            if '/series/' not in link:
                yield scrapy.Request(url=self.get_next_page_url(link, page + 1), callback=self.parse_token, meta={'page': page, 'url': link})
            else:
                yield scrapy.Request(link, callback=self.parse_token, meta={'page': page, 'url': link})

    def get_next_page_url(self, base, page):
        matches = ['isthisreal', 'touchmywife', 'zerotolerance', 'povthis', 'tabooheat', 'puretaboo', 'pridestudios', 'prettydirty', 'gangbangcreampie']
        if any(x in base for x in matches):
            pagination = '/en/videos/page/%s'
        else:
            pagination = self.get_selector_map('pagination')
        if int(page) == 1:
            return self.format_url(base, '/en/videos')
        url = self.format_url(base, pagination % page)
        return url

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia(response.meta['page'], token, response.meta['url'])

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    next_page = response.meta['page'] + 1
                    yield self.call_algolia(next_page, response.meta['token'], response.meta['url'])

    def get_scenes(self, response):
        # ~ print(response.json()['results'])
        referrerurl = response.meta["url"]
        for scene in response.json()['results'][0]['hits']:
            # ~ if 'upcoming' in scene and scene['upcoming'] == 1:
            # ~ continue
            item = SceneItem()

            force_update = self.settings.get('force_update')
            if force_update:
                force_update = True
            force_fields = self.settings.get('force_fields')
            if force_fields:
                force_fields = force_fields.split(",")

            if not force_update or (force_update and "image" in force_fields):
                item['image'] = ''
                for size in self.image_sizes:
                    if size in scene['pictures']:
                        item['image'] = 'https://images-fame.gammacdn.com/movies' + \
                                        scene['pictures'][size]
                        break

                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                # ~ item['image_blob'] = None
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['trailer'] = ''
            if "trailers" in scene and scene['trailers']:
                for size in self.trailer_sizes:
                    if size in scene['trailers']:
                        item['trailer'] = scene['trailers'][size]
                        break

            item['id'] = scene['objectID'].split('-')[0]

            if 'title' in scene and scene['title']:
                item['title'] = scene['title']
            else:
                item['title'] = scene['movie_title']

            item['title'] = string.capwords(item['title'])

            if 'description' in scene:
                item['description'] = scene['description']
            elif 'description' in scene['_highlightResult']:
                item['description'] = scene['_highlightResult']['description']['value']
            if 'description' not in item:
                item['description'] = ''

            if self.parse_date(scene['release_date']):
                item['date'] = self.parse_date(scene['release_date']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = list(
                map(lambda x: x['name'], scene['actors']))
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))

            item['duration'] = str(scene['length'])

            if "directors" in scene and len(scene['directors']):
                item['director'] = scene['directors'][0]['name']

            item['markers'] = []
            if 'action_tags' in scene:
                if scene['action_tags']:
                    for action in scene['action_tags']:
                        marker = {}
                        marker['name'] = action['name']
                        if marker['name'] not in item['tags']:
                            item['tags'].append(marker['name'])
                        marker['start'] = str(action['timecode'])
                        item['markers'].append(marker)

            item['site'] = scene['sitename']
            item['site'] = match_site(item['site'])
            item['network'] = self.network
            if '21sextreme' in referrerurl:
                item['parent'] = "21Sextreme"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if '21sextury' in referrerurl:
                item['parent'] = "21Sextury"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if '21naturals' in referrerurl:
                item['parent'] = "21Naturals"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'activeduty' in referrerurl:
                item['parent'] = "Active Duty"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'adam-and-eve' in referrerurl:
                item['parent'] = "Adam and Eve Pictures"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'addicted2girls' in referrerurl:
                item['parent'] = "Addicted2Girls"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'asmr-fantasy' in referrerurl:
                item['parent'] = "ASMR Fantasy"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'ageandbeauty' in referrerurl:
                item['parent'] = "Age And Beauty"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'agentredgirl' in referrerurl:
                item['parent'] = "Agent Red Girl"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'biphoria' in referrerurl:
                item['parent'] = "BiPhoria"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'blowpass' in referrerurl:
                item['parent'] = "BlowPass"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'couple-swapping' in referrerurl:
                item['parent'] = "Couple Swapping"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'chaosmen' in referrerurl:
                item['parent'] = "Chaos Men"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'diabolic' in referrerurl:
                item['parent'] = "Diabolic"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'devilsfilm' in referrerurl:
                item['parent'] = "Devils Film"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'dfxtra' in referrerurl:
                item['network'] = "dogfartnetwork"
                item['site'] = scene['serie_name']
                item['parent'] = "dogfartnetwork"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'downlowboys' in referrerurl:
                item['parent'] = "Downlow Boys"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
                item['tags'].append("Gay")
            if 'dpfanatics' in referrerurl:
                item['parent'] = "Devils Film"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'clubinfernodungeon' in referrerurl:
                item['parent'] = "Club Inferno Dungeon"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'evilangel' in referrerurl:
                item['parent'] = "Evil Angel"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'falconstudios' in referrerurl:
                item['network'] = "Falcon Studios"
                item['site'] = scene['studio_name']
                item['parent'] = "Falcon Studios"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'famedigital' in referrerurl:
                item['parent'] = "Fame Digital"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'fantasymassage' in referrerurl:
                item['parent'] = "Fantasy Massage"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'femboyish' in referrerurl:
                item['parent'] = "Femboyish"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'filthykings' in referrerurl:
                item['parent'] = "Filthy Kings"
                item['site'] = scene['serie_name']
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'footsiebabes' in referrerurl:
                item['parent'] = "Footsie Babes"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'gangbangcreampie' in referrerurl:
                item['parent'] = "Gangbang Creampie"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'genderx' in referrerurl:
                item['parent'] = "Gender X"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'girlfriendsfilms' in referrerurl:
                item['parent'] = "Girlfriends Films"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'girlsway' in referrerurl:
                item['parent'] = "Girlsway"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'gloryholesecrets' in referrerurl:
                item['parent'] = "Gloryhole Secrets"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'interracialvision' in referrerurl:
                item['parent'] = "Interracialvision"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'jerk-buddies' in referrerurl:
                item['parent'] = "Jerk Buddies"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'joymii' in referrerurl:
                item['parent'] = "JoyMii"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'kiss-me-fuck-me' in referrerurl:
                item['parent'] = "Kiss Me Fuck Me"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'ladygonzo' in referrerurl:
                item['parent'] = "Lady Gonzo"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'lethalhardcore' in referrerurl:
                item['parent'] = "Lethal Hardcore"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'lez-be-bad' in referrerurl:
                item['parent'] = "Lez Be Bad"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'lewood' in referrerurl:
                item['parent'] = "Lewood"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'mixedx' in referrerurl:
                item['parent'] = "Mixed X"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'modeltime' in referrerurl:
                item['parent'] = "Model Time"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'moderndaysins' in referrerurl:
                item['parent'] = "Modern Day Sins"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'isthisreal' in referrerurl:
                item['parent'] = "Is This Real"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'mommysgirl' in referrerurl:
                item['parent'] = "Mommys Girl"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'mypervyfamily' in referrerurl:
                item['parent'] = "My Pervy Family"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'naked-yoga-life' in referrerurl:
                item['parent'] = "Naked Yoga Life"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'nextdoorstudios' in referrerurl:
                item['parent'] = "Next Door Studios"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'oopsie' in referrerurl:
                item['parent'] = "Oopsie"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'peternorth' in referrerurl:
                item['parent'] = "Peter North"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'povthis' in referrerurl:
                item['parent'] = "POV This"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'prettydirty' in referrerurl:
                item['parent'] = "Pretty Dirty"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'pridestudios' in referrerurl:
                item['parent'] = "Pride Studios"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'puretaboo' in referrerurl:
                item['parent'] = "Pure Taboo"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'puretaboo' in referrerurl:
                item['parent'] = "Pure Taboo"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'ragingstallion' in referrerurl:
                item['parent'] = "Raging Stallion Studios"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'roccosiffredi' in referrerurl:
                item['parent'] = "Rocco Siffredi"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'shower-solos' in referrerurl:
                item['parent'] = "Shower Solos"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'shapeofbeauty' in referrerurl:
                item['parent'] = "Shape of Beauty"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'she-wants-him' in referrerurl:
                item['parent'] = "She Wants Him"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'tabooheat' in referrerurl:
                item['parent'] = "Taboo Heat"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'teen-sneaks' in referrerurl:
                item['parent'] = "Teen Sneaks"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'thebrats' in referrerurl:
                item['parent'] = "Teen Sneaks"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'the-mike-and-joanna-show' in referrerurl:
                item['parent'] = "The Mike and Joanna Show"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'with-love-lexi' in referrerurl:
                item['parent'] = "With Love Lexi"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'switch' in referrerurl:
                if item['site'].lower() == "switch":
                    item['parent'] = "Switch"
                else:
                    item['parent'] = item['site']
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'touchmywife' in referrerurl:
                item['parent'] = "Touch My Wife"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'transfixed' in referrerurl:
                item['parent'] = "Transfixed"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'transsexualroadtrip' in referrerurl:
                item['parent'] = "Transsexual Roadtrip"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'truelesbian' in referrerurl:
                item['site'] = "True Lesbian"
                item['parent'] = "True Lesbian"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'tsfactor' in referrerurl:
                item['site'] = "TS Factor"
                item['parent'] = "TS Factor"
                item['url'] = self.format_url(response.meta['url'], '/en/video/evilangel/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'vivid' in referrerurl:
                item['parent'] = "Vivid"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'wicked' in referrerurl:
                item['parent'] = "Wicked"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'xempire' in referrerurl or 'allblackx' in referrerurl or 'darkx' in referrerurl or 'eroticax' in referrerurl or 'hardx' in referrerurl or 'lesbianx' in referrerurl:
                item['parent'] = "XEmpire"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'zerotolerance' in referrerurl:
                item['parent'] = "Zero Tolerance"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))

            #  The following sites were brought in from other scrapers.  Date limits are to avoid dupes
            donotyield = 0
            if (('mypervyfamily' in item['url'] and item['date'] < "2021-10-06") or ('Filthy Blowjobs' in item['site'] and item['date'] < "2021-09-14") or ('Filthy Massage' in item['site'] and item['date'] < "2021-09-28") or ('Filthy Newbies' in item['site'] and item['date'] < "2021-09-21") or ('Filthy POV' in item['site'] and item['date'] < "2021-10-05") or ('Filthy Taboo' in item['site'] and item['date'] < "2021-10-09")):
                donotyield = 1

            if ('Falcon Studios' in item['network'] and item['date'] < "2023-04-01"):
                donotyield = 1

            if ('TS Factor' in item['site'] and item['date'] < "2021-11-24"):
                donotyield = 1

            if ('activeduty' in item['url'] and item['date'] < "2023-02-20"):
                donotyield = 1

            # ~ if ('gangbangcreampie' in item['url'] and item['date'] < "2022-10-29"):
                # ~ donotyield = 1

            if ('gloryholesecrets' in item['url'] and item['date'] < "2022-10-01"):
                donotyield = 1

            if ('jerk-buddies' in item['url'] and item['date'] < "2024-04-01"):
                donotyield = 1

            if (('Lusty Grandmas' in item['site'] and item['date'] < "2019-02-01") or ('Grandpas Fuck Teens' in item['site'] and item['date'] < "2019-02-06") or ('Baby Got Balls' in item['site'] and item['date'] < "2008-05-04") or ('Creampie Reality' in item['site'] and item['date'] < "2006-10-04") or ('Cumming Matures' in item['site'] and item['date'] < "2009-12-01")):
                donotyield = 1

            if (('Dominated Girls' in item['site'] and item['date'] < "2013-08-26") or ('Home Porn Reality' in item['site'] and item['date'] < "2010-06-18") or ('Mandy Is Kinky' in item['site'] and item['date'] < "2008-04-30") or ('Mighty Mistress' in item['site'] and item['date'] < "2014-05-20") or ('Teach Me Fisting' in item['site'] and item['date'] < "2019-01-29") or ('Zoliboy' in item['site'] and item['date'] < "2018-03-18") or ('Pee And Blow' in item['site'] and item['date'] < "2009-12-16") or ('Speculum Plays' in item['site'] and item['date'] < "2007-09-07")):
                donotyield = 1

            #  Old Young Lesbian Love is returned both from Girlsway and 21Sextreme.  Only pull from Girlsway
            if "oldyounglesbianlove" in scene['sitename'] and "21sextreme" in referrerurl:
                donotyield = 1

            matches = ['evilangelpartner', 'nudefightclub']
            if not any(x in scene['sitename'] for x in matches):
                if not donotyield:
                    yield self.check_item(item, self.days)

    def call_algolia(self, page, token, referrer):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }

        if "ragingstallion" in referrer:
            algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(17.0.2)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token
        elif "falconstudios" in referrer:
            algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.27.1%3BJS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token
            headers['Referer'] = 'https://www.falconstudios.com'
        else:
            algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        if '21sextreme' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3A21sextreme%22%2C%22availableOnSite%3Alustygrandmas%22%2C%22availableOnSite%3Agrandpasfuckteens%22%2C%22availableOnSite%3Ababygotballs%22%2C%22availableOnSite%3Acreampiereality%22%2C%22availableOnSite%3Acummingmatures%22%2C%22availableOnSite%3Adominatedgirls%22%2C%22availableOnSite%3Ahomepornreality%22%2C%22availableOnSite%3Amandyiskinky%22%2C%22availableOnSite%3Amightymistress%22%2C%22availableOnSite%3Apeeandblow%22%2C%22availableOnSite%3Aspeculumplays%22%2C%22availableOnSite%3Ateachmefisting%22%2C%22availableOnSite%3Atransfrombrazil%22%2C%22availableOnSite%3Atranssmuts%22%2C%22availableOnSite%3Azoliboy%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22description%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if '21sextury' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3A21sextury%22%2C%22availableOnSite%3Aanalteenangels%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Aalettaoceanempire%22%2C%22availableOnSite%3Aassholefever%22%2C%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3Aanalqueenalysa%22%2C%22availableOnSite%3Ablueangellive%22%2C%22availableOnSite%3Abuttplays%22%2C%22availableOnSite%3Acheatingwhorewives%22%2C%22availableOnSite%3Aclubsandy%22%2C%22availableOnSite%3Acutiesgalore%22%2C%22availableOnSite%3Adeepthroatfrenzy%22%2C%22availableOnSite%3Agapeland%22%2C%22availableOnSite%3Ahotmilfclub%22%2C%22availableOnSite%3Aletsplaylez%22%2C%22availableOnSite%3Aonlyswallows%22%2C%22availableOnSite%3Apixandvideo%22%2C%22availableOnSite%3Asexwithkathianobili%22%2C%22availableOnSite%3Asweetsophiemoone%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3A21sextury%22%2C%22availableOnSite%3Aanalteenangels%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Aalettaoceanempire%22%2C%22availableOnSite%3Aassholefever%22%2C%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3Aanalqueenalysa%22%2C%22availableOnSite%3Ablueangellive%22%2C%22availableOnSite%3Abuttplays%22%2C%22availableOnSite%3Acheatingwhorewives%22%2C%22availableOnSite%3Aclubsandy%22%2C%22availableOnSite%3Acutiesgalore%22%2C%22availableOnSite%3Adeepthroatfrenzy%22%2C%22availableOnSite%3Agapeland%22%2C%22availableOnSite%3Ahotmilfclub%22%2C%22availableOnSite%3Aletsplaylez%22%2C%22availableOnSite%3Aonlyswallows%22%2C%22availableOnSite%3Apixandvideo%22%2C%22availableOnSite%3Asexwithkathianobili%22%2C%22availableOnSite%3Asweetsophiemoone%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if '21naturals' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3A21naturals%22%2C%22availableOnSite%3A21eroticanal%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'activeduty' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aactiveduty%22%2C%22availableOnSite%3Aactivedutypartners%22%2C%22availableOnSite%3Astagcollectivesolos%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'adam-and-eve' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Aadamandevepictures%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'addicted2girls' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22studio_name%22%2C%22serie_name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22download_sizes%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'ageandbeauty' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aageandbeauty%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'agentredgirl' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22content_tags%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22content_tags%3Atrans%22%5D%2C%5B%22availableOnSite%3Aagentredgirl%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_tags&facetFilters=%5B%5B%22availableOnSite%3Aagentredgirl%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22content_tags%3Atrans%22%5D%5D"}]}'
        if 'allblackx.com' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aallblackx%22%5D%5D"}]}'
        if 'asmr-fantasy' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Aasmrfantasy%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'biphoria' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'blowpass' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ablowpass%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Athroated%22%2C%22availableOnSite%3Aonlyteenblowjobs%22%2C%22availableOnSite%3A1000facials%22%2C%22availableOnSite%3Aimmorallive%22%2C%22availableOnSite%3Amommyblowsbest%22%2C%22availableOnSite%3Asunlustxxx%22%2C%22availableOnSite%3Asquirtingorgies%22%2C%22availableOnSite%3Ablowbanged%22%2C%22availableOnSite%3Ablowpass%22%2C%22availableOnSite%3Ablowpasspartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ablowpass%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Athroated%22%2C%22availableOnSite%3Aonlyteenblowjobs%22%2C%22availableOnSite%3A1000facials%22%2C%22availableOnSite%3Aimmorallive%22%2C%22availableOnSite%3Amommyblowsbest%22%2C%22availableOnSite%3Asunlustxxx%22%2C%22availableOnSite%3Asquirtingorgies%22%2C%22availableOnSite%3Ablowbanged%22%2C%22availableOnSite%3Ablowpass%22%2C%22availableOnSite%3Ablowpasspartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ablowpass%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'chaosmen' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22categories.name%22%5D&tagFilters="}]}'
        if 'couple-swapping' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Acoupleswapping%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'evilangel' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aevilangel%22%2C%22context%3Avideos%22%2C%22device%3Amobile%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=compilation%3A%200&facets=%5B%22content_tags%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aevilangel%22%2C%22context%3Avideos%22%2C%22device%3Amobile%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=compilation%3A%200&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'fantasymassage' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Anurumassage%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Asoapymassage%22%2C%22availableOnSite%3Amassage-parlor%22%2C%22availableOnSite%3Amilkingtable%22%2C%22availableOnSite%3Afantasymassage%22%2C%22availableOnSite%3Atrickyspa%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'darkx.com' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Adarkx%22%5D%5D"}]}'
        if 'devilsfilm' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Asquirtalicious%22%2C%22availableOnSite%3Ahairyundies%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Adevilsfilmparodies%22%2C%22availableOnSite%3Agivemeteens%22%2C%22availableOnSite%3Aoutofthefamily%22%2C%22availableOnSite%3Adevilsgangbangs%22%2C%22availableOnSite%3AJaneDoePictures%22%2C%22availableOnSite%3Adevilstgirls%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'diabolic' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adiabolic%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Adiabolic%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adiabolic%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Adiabolic%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adiabolic%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'dfxtra' in referrer:
            # ~ jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Adfxtra%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\')&facets=%5B%22channels.name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22categories.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Adfxtra%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\')&facets=%5B%22channels.name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22categories.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'downlowboys' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adownlowboys%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.name%22%5D&filters=(availableOnSite%3A\'downlowboys\')%20AND%20(NOT%20categories.name%3A\'Behind%20The%20Scene\')%20AND%20(upcoming%3A\'0\')%20AND%20availableOnSite%3Adownlowboys&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'
        if 'dpfanatics' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adpfanatics%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Adpfanatics%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adpfanatics%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Adpfanatics%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adpfanatics%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'eroticax.com' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aeroticax%22%5D%5D"}]}'
        if 'falconstudios' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&page=' + str(page) + '&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22sitename%3A-nakedsword%22%2C%22categories.name%3A-Behind%20The%20Scenes%22%2C%22categories.name%3A-Compilation%22%2C%22categories.name%3A-Enhanced%22%2C%22upcoming%3A0%22%2C%5B%22availableOnSite%3Afalconstudios%22%2C%22availableOnSite%3Ahothouse%22%2C%22availableOnSite%3Afalconstudiospartners%22%5D%5D"}]}'
        if 'famedigital' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afamedigital%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Asilverstonedvd%22%2C%22availableOnSite%3Asilviasaint%22%2C%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Awhiteghetto%22%2C%22availableOnSite%3Apeternorth%22%2C%22availableOnSite%3Aterapatrick%22%2C%22availableOnSite%3Afamedigital%22%2C%22availableOnSite%3Aroccosiffredi%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Amyteenoasis%22%2C%22availableOnSite%3Adaringsex%22%2C%22availableOnSite%3Alowartfilms%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afamedigital%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Asilverstonedvd%22%2C%22availableOnSite%3Asilviasaint%22%2C%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Awhiteghetto%22%2C%22availableOnSite%3Apeternorth%22%2C%22availableOnSite%3Aterapatrick%22%2C%22availableOnSite%3Afamedigital%22%2C%22availableOnSite%3Aroccosiffredi%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Amyteenoasis%22%2C%22availableOnSite%3Adaringsex%22%2C%22availableOnSite%3Alowartfilms%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afamedigital%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'femboyish' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Afemboyish%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'filthykings' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afilthykings%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afilthykings%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'footsiebabes' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afootsiebabes%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afootsiebabes%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afootsiebabes%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'gangbangcreampie' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Agangbangcreampie%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'genderx' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Agenderx%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20site_id%3A428&facets=%5B%22categories.name%22%2C%22actors.name%22%2C%22serie_name%22%2C%22length_range_15min%22%2C%22download_sizes%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Agenderx%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20site_id%3A428&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'girlfriendsfilms' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Agirlfriendsfilms%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20categories.name%3A\'Compilation\'%20AND%20NOT%20categories.name%3A\'Member%20Compilation\')&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3A-girlfriendsfilmspartners%22%5D%5D"}]}'
        if 'girlsway' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Awebyoung%22%2C%22availableOnSite%3Agirlsway%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlstryanal%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Asquirtinglesbian%22%2C%22availableOnSite%3Aoldyounglesbianlove%22%2C%22availableOnSite%3Agirlcore%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Alesbianrevenge%22%2C%22availableOnSite%3Amomsonmoms%22%2C%22availableOnSite%3Awheretheboysarent%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Awebyoung%22%2C%22availableOnSite%3Agirlsway%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlstryanal%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Asquirtinglesbian%22%2C%22availableOnSite%3Aoldyounglesbianlove%22%2C%22availableOnSite%3Agirlcore%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Alesbianrevenge%22%2C%22availableOnSite%3Amomsonmoms%22%2C%22availableOnSite%3Awheretheboysarent%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
            # ~ jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Adfxtra%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\')&facets=%5B%22channels.name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22categories.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%22categories.name%3ABehind%20The%20Scene%22%2C%5B%22upcoming%3A0%22%5D%2C%5B%22categories.name%3ABehind%20The%20Scene%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Adfxtra%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\')&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%22categories.name%3ABehind%20The%20Scene%22%2C%5B%22categories.name%3ABehind%20The%20Scene%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Adfxtra%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\')&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=categories.name&facetFilters=%5B%22categories.name%3ABehind%20The%20Scene%22%2C%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'gloryholesecrets' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Agloryholesecrets%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'interracialvision' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ainterracialvision%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Ainterracialvision%22%5D%5D"}]}'
        if 'isthisreal' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Atrickyspa%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlsunderarrest%22%2C%22availableOnSite%3Abethecuck%22%2C%22availableOnSite%3Asistertrick%22%2C%22availableOnSite%3Aisthisreal%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'hardx.com' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Ahardx%22%5D%5D"}]}'
        if 'jerk-buddies' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ajerkbuddies%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.name%22%5D&filters=(upcoming%3A\'0\')%20AND%20availableOnSite%3Ajerk-buddies&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'
        if 'joymii' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ajoymii%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Ajoymii%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ajoymii%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Ajoymii%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ajoymii%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'kiss-me-fuck-me' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Akissmefuckme%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'ladygonzo' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aladygonzo%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'lesbianx.com' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Alesbianx%22%5D%5D"}]}'
        if 'lethalhardcore.com' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Alethalhardcore%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22categories.name%3A-VR%22%5D%2C%5B%22availableOnSite%3Alethalhardcore%22%2C%22availableOnSite%3Alethalhardcorevr%22%5D%5D"}]}'
        if 'lethalhardcorevr' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Alethalhardcorevr%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(availableOnSite%3A\'lethalhardcorevr\')&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Alethalhardcorevr%22%5D%5D"}]}'
        if 'lewood' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Alewood%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Alewood%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Alewood%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Alewood%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Alewood%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'lez-be-bad' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22network.lvl0%22%2C%22network.lvl1%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22network.lvl1%3AAdult%20Time%20Originals%20%3E%20Lez%20Be%20Bad%22%5D%5D"}]}'
        if 'mixedx' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=12&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Amixedx%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'modeltime' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Amodeltime%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Amodeltime%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'moderndaysins' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amoderndaysins%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Amoderndaysins%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amoderndaysins%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Amoderndaysins%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amoderndaysins%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'mommysgirl' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amommysgirl%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Amommysgirl%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amommysgirl%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Amommysgirl%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amommysgirl%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'mypervyfamily' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amypervyfamily%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amypervyfamily%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'naked-yoga-life' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Anakedyogalife%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'peternorth' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apeternorth%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Apeternorth%22%5D%5D"},{"indexName":"all_scenes_latest_desc"]}'
        if 'clubinfernodungeon' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=20&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22studio_name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22download_sizes%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'nextdoorstudios' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Anextdoorstudios%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A107%20AND%20NOT%20site_id%3A%20118%20AND%20NOT%20serie_name%3A\'Member%20Compilations\'&facets=%5B%22categories.name%22%2C%22actors.name%22%2C%22sitename%22%2C%22length_range_15min%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Anextdoorstudios%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A107%20AND%20NOT%20site_id%3A%20118%20AND%20NOT%20serie_name%3A\'Member%20Compilations\'&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'oopsie' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Aoopsie%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'povthis' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apovthis%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Apovthis%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apovthis%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Apovthis%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apovthis%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'prettydirty' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aprettydirty%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Aprettydirty%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aprettydirty%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Aprettydirty%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aprettydirty%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'pridestudios' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apridestudios%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22sitename%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apridestudios%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'puretaboo' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Apuretaboo%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Apuretaboo%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'ragingstallion' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aragingstallion%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20studio_name%3A\'Naked%20Sword%20Originals\'%20AND%20NOT%20studio_name%3A\'Fetish%20Force\'%20AND%20NOT%20studio_name%3A\'Hot%20House\'%20AND%20NOT%20studio_name%3A\'Falcon%20Studios\')&facets=%5B%22availableOnSite%22%2C%22categories.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22categories.name%3A-Backstage%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aragingstallion%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(NOT%20studio_name%3A\'Naked%20Sword%20Originals\'%20AND%20NOT%20studio_name%3A\'Fetish%20Force\'%20AND%20NOT%20studio_name%3A\'Hot%20House\'%20AND%20NOT%20studio_name%3A\'Falcon%20Studios\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22categories.name%3A-Backstage%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aragingstallion%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(NOT%20studio_name%3A\'Naked%20Sword%20Originals\'%20AND%20NOT%20studio_name%3A\'Fetish%20Force\'%20AND%20NOT%20studio_name%3A\'Hot%20House\'%20AND%20NOT%20studio_name%3A\'Falcon%20Studios\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=categories.name&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'roccosiffredi' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=12&page=' + str(page) + '&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Aroccosiffredi%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'she-wants-him' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Ashewantshim%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'shapeofbeauty' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ashapeofbeauty%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.name%22%5D&filters=(upcoming%3A\'0\')%20AND%20availableOnSite%3Ashapeofbeauty&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=0&query=&tagFilters="}]}'
        if 'tabooheat' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'shower-solos' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Ashowersolos%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'switch' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3ASwitch%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'teen-sneaks' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Ateensneaks%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'thebrats' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=24&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Athebrats%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'the-mike-and-joanna-show' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22availableOnSite%3Athemikeandjoannashow%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&facets=availableOnSite&facetFilters=%5B%22upcoming%3A0%22%5D"}]}'
        if 'touchmywife' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atouchmywife%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atouchmywife%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'transfixed' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atranssexualroadtrip%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Atranssexualroadtrip%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atranssexualroadtrip%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Atranssexualroadtrip%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atranssexualroadtrip%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'transsexualroadtrip' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22content_tags%22%2C%22upcoming%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22content_tags%3Atrans%22%5D%2C%5B%22availableOnSite%3AAburningangel%22%2C%22availableOnSite%3Apuretaboo%22%2C%22availableOnSite%3Atransfixed%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Amodeltime%22%2C%22availableOnSite%3ABeingTrans247%22%2C%22availableOnSite%3ATransgressiveFilms%22%5D%5D"},{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22content_tags%3Atrans%22%5D%2C%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Aburningangel%22%2C%22availableOnSite%3Apuretaboo%22%2C%22availableOnSite%3Atransfixed%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Amodeltime%22%2C%22availableOnSite%3ABeingTrans247%22%2C%22availableOnSite%3ATransgressiveFilms%22%5D%5D"},{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_tags&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Aburningangel%22%2C%22availableOnSite%3Apuretaboo%22%2C%22availableOnSite%3Atransfixed%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Amodeltime%22%2C%22availableOnSite%3ABeingTrans247%22%2C%22availableOnSite%3ATransgressiveFilms%22%5D%5D"},{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22content_tags%3Atrans%22%5D%5D"}]}'
        if 'truelesbian' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atruelesbian%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.name%22%5D&filters=(upcoming%3A\'0\')%20AND%20availableOnSite%3Atruelesbian&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=0&query=&tagFilters="}]}'
        if 'tsfactor' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atsfactor%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Ashemaleidol%22%2C%22availableOnSite%3Atsfactor%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atsfactor%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Ashemaleidol%22%2C%22availableOnSite%3Atsfactor%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atsfactor%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'with-love-lexi' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3AWith%20Love%2C%20Lexi%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'wicked' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Awicked%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A427%20AND%20NOT%20serie_name%3A%27Member%20Compilations%27&facets=%5B%22categories.name%22%2C%22directors.name%22%2C%22female_actors.name%22%2C%22serie_name%22%2C%22length_range_15min%22%2C%22download_sizes%22%2C%22genres.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Awicked%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A427%20AND%20NOT%20serie_name%3A%27Member%20Compilations%27&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'vivid' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Atour1%22%2C%22site%3Avivid%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.url_name%22%2C%22sitename%22%5D&filters=(upcoming%3A\'0\')%20AND%20availableOnSite%3Avividgirls%20OR%20availableOnSite%3A65inchhugeasses%20OR%20availableOnSite%3Ablackwhitefuckfest%20OR%20availableOnSite%3Abrandnewfaces%20OR%20availableOnSite%3Agirlswhofuckgirls%20OR%20availableOnSite%3Amomisamilf%20OR%20availableOnSite%3Anastystepfamily%20OR%20availableOnSite%3Anineteen%20OR%20availableOnSite%3Aorgytrain%20OR%20availableOnSite%3Apetited%20OR%20availableOnSite%3Avivid%20OR%20availableOnSite%3Avividceleb%20OR%20availableOnSite%3Avividclassic%20OR%20availableOnSite%3Atsdivas%20OR%20availableOnSite%3Awheretheboysarent%20OR%20availableOnSite%3Athebrats&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'
        if 'xempire' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Axempire%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=compilation%3A%200&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Aeroticax%22%2C%22availableOnSite%3Ahardx%22%2C%22availableOnSite%3Adarkx%22%2C%22availableOnSite%3Alesbianx%22%2C%22availableOnSite%3Axempire%22%2C%22availableOnSite%3Aallblackx%22%2C%22availableOnSite%3Axempirepartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Axempire%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=compilation%3A%200&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Aeroticax%22%2C%22availableOnSite%3Ahardx%22%2C%22availableOnSite%3Adarkx%22%2C%22availableOnSite%3Alesbianx%22%2C%22availableOnSite%3Axempire%22%2C%22availableOnSite%3Aallblackx%22%2C%22availableOnSite%3Axempirepartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Axempire%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=compilation%3A%200&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'zerotolerance' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22serie_name%22%2C%22actors.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta={'token': token, 'page': page, 'url': referrer},
            callback=self.parse,
            headers=headers
        )
