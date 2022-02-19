import re
from datetime import date, timedelta
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
        'addicted2girls': 'Addicted2Girls',
        'adulttime': 'AdultTime',
        'agentredgirl': 'Agent Red Girl',
        'alettaoceanempire': 'Aletta Ocean Empire',
        'allgirlmassage': 'All Girl Massage',
        'analqueenalysa': 'Anal Queen Alysa',
        'analteenangels': 'Anal Teen Angels',
        'assholefever': 'Asshole Fever',
        'austinwilde': 'Austin Wilde',
        'babygotballs': 'Baby Got Balls',
        'biphoria': 'BiPhoria',
        'bethecuck': 'Be The Cuck',
        'blueangellive': 'Blue Angel Live',
        'burningangel': 'Burning Angel',
        'buttplays': 'Buttplays',
        'cheatingwhorewives': 'Cheating Whore Wives',
        'clubinfernodungeon': 'Club Inferno Dungeon',
        'clubsandy': 'Club Sandy',
        'codycummings': 'Cody Cummings',
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
        # 'dpfanatics': 'DPFanatics', Pulled from Gamma
        'evilangel': 'Evil Angel',
        'fantasymassage': 'Fantasy Massage',
        'femalesubmission': 'Female Submission',
        'footsiebabes': 'Footsie Babes',
        'gapeland': 'Gapeland',
        'genderx': 'Gender X',
        'girlcore': 'Girlcore',
        'girlsunderarrest': 'Girls Under Arrest',
        'girlstryanal': 'Girls Try Anal',
        'girlsway': 'Girlsway',
        'givemeteens': 'Give Me Teens',
        'grandpasfuckteens': 'Grandpas Fuck Teens',
        'hairyundies': 'Hairy Undies',
        'homepornreality': 'Home Porn Reality',
        'hotmilfclub': 'Hot MILF Club',
        'isthisreal': 'Is This Real',
        'JaneDoePictures': 'Jane Doe Pictures',
        'lesbianfactor': 'Lesbian Factor',
        'letsplaylez': 'Lets Play Lez',
        'lezcuties': 'Lez Cuties',
        'lustygrandmas': 'Lusty Grandmas',
        'mandyiskinky': 'Mandy Is Kinky',
        'marcusmojo': 'Marcus Mojo',
        'masonwyler': 'Mason Wyler',
        'massageparlor': 'Massage Parlor',
        'mightymistress': 'Mighty Mistress',
        'modeltime': 'Model Time',
        'moderndaysins': 'Modern Day Sins',
        'mommysgirl': 'Mommys Girl',
        'momsonmoms': 'Moms on Moms',
        'mypervyfamily': 'My Pervy Family',
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
        'puretaboo': 'Pure Taboo',
        'roddaily': 'Rod Daily',
        'samuelotoole': 'Samuel Otoole',
        'sistertrick': 'Sister Trick',
        'sextapelesbians': 'Sextape Lesbians',
        'sexwithkathianobili': 'Sex With Kathia Nobili',
        'soapymassage': 'Soapy Massage',
        'speculumplays': 'Speculum Plays',
        'squirtalicious': 'Squirtalicious',
        'stagcollectivesolos': 'Stag Collective Solos',
        'strokethatdick': 'Stroke That Dick',
        'sweetsophiemoone': 'Sweet Sophie Moon',
        'tabooheat': 'Taboo Heat',
        'teachmefisting': 'Teach Me Fisting',
        'tommydxxx': 'Tommy D XXX',
        'touchmywife': 'Touch My Wife',
        'transfixed': 'Transfixed',
        'trickyspa': 'Tricky Spa',
        'transfrombrazil': 'Trans From Brazil',
        'TransgressiveFilms': 'Transgressive Films',
        'transsmuts': 'Trans Smuts',
        'truelesbian.com': 'True Lesbian',
        'trystanbull': 'Trystan Bull',
        'webyoung': 'Web Young',
        'welikegirls': 'We Like Girls',
        'wheretheboysarent': 'Where the Boys Arent',
        'wicked': 'Wicked',
        'zerotolerancefilms': 'Zero Tolerance',
        'zoliboy': 'Zoliboy',
    }
    return match.get(argument, argument)


class AdultTimeAPISpider(BaseSceneScraper):
    name = 'AdulttimeAPI'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://www.21sextreme.com',
        'https://www.21sextury.com',
        'https://www.21naturals.com',
        'https://www.addicted2girls.com',
        # ~ ## 'https://www.agentredgirl.com', Disabled due to AdultTime being very protective
        'https://www.biphoria.com',
        'https://www.clubinfernodungeon.com',
        'https://www.devilsfilm.com',
        'https://www.diabolic.com',
        'https://www.evilangel.com',
        'https://www.fantasymassage.com',
        'https://www.filthykings.com',
        'https://www.genderx.com',
        'https://www.girlsway.com',
        'https://www.isthisreal.com',
        'https://www.modeltime.com',
        'https://www.moderndaysins.com',
        'https://www.mommysgirl.com',
        'https://www.mypervyfamily.com',
        'https://www.nextdoorstudios.com',
        'https://www.puretaboo.com',
        'https://www.tabooheat.com',
        'https://www.touchmywife.com',
        'https://www.transfixed.com',
        'https://www.wicked.com',
        'https://www.zerotolerancefilms.com',
    ]

    image_sizes = [
        '1920x1080',
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

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/en/videos?page=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, 1), callback=self.parse_token,
                                 meta={'page': 0, 'url': link})

    def get_next_page_url(self, base, page):
        if "isthisreal" in base or "touchmywife" in base or "zerotolerance" in base:
            pagination = '/en/videos/page/%s'
        else:
            pagination = self.get_selector_map('pagination')
        return self.format_url(base, pagination % page)

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia(0, token, response.meta['url'])

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
            if 'upcoming' in scene and scene['upcoming'] == 1:
                continue

            item = SceneItem()

            item['image'] = ''
            for size in self.image_sizes:
                if size in scene['pictures']:
                    item['image'] = 'https://images-fame.gammacdn.com/movies' + \
                                    scene['pictures'][size]
                    break

            item['image_blob'] = None

            item['trailer'] = ''
            for size in self.trailer_sizes:
                if size in scene['trailers']:
                    item['trailer'] = scene['trailers'][size]
                    break

            item['id'] = scene['objectID'].split('-')[0]

            if 'title' in scene and scene['title']:
                item['title'] = scene['title']
            else:
                item['title'] = scene['movie_title']

            item['description'] = scene['description']
            if self.parse_date(scene['release_date']):
                item['date'] = self.parse_date(scene['release_date']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = list(
                map(lambda x: x['name'], scene['actors']))
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))

            item['site'] = scene['sitename']
            item['site'] = match_site(item['site'])
            item['network'] = self.network
            if '21sextreme' in referrerurl:
                item['parent'] = "21Sextreme"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if '21sextury' in referrerurl:
                item['parent'] = "21Sextury"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if '21naturals' in referrerurl:
                item['parent'] = "21Naturals"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'addicted2girls' in referrerurl:
                item['parent'] = "Addicted2Girls"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'agentredgirl' in referrerurl:
                item['parent'] = "Agent Red Girl"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'biphoria' in referrerurl:
                item['parent'] = "BiPhoria"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'diabolic' in referrerurl:
                item['parent'] = "Diabolic"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'devilsfilm' in referrerurl:
                item['parent'] = "Devils Film"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'clubinfernodungeon' in referrerurl:
                item['parent'] = "Club Inferno Dungeon"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'evilangel' in referrerurl:
                item['parent'] = "Evil Angel"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'fantasymassage' in referrerurl:
                item['parent'] = "Fantasy Massage"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'filthykings' in referrerurl:
                item['parent'] = "Filthy Kings"
                item['site'] = scene['serie_name']
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'genderx' in referrerurl:
                item['parent'] = "Gender X"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'girlsway' in referrerurl:
                item['parent'] = "Girlsway"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
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
            if 'nextdoorstudios' in referrerurl:
                item['parent'] = "Next Door Studios"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'puretaboo' in referrerurl:
                item['parent'] = "Taboo Heat"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'tabooheat' in referrerurl:
                item['parent'] = "Pure Taboo"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'touchmywife' in referrerurl:
                item['parent'] = "Touch My Wife"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'transfixed' in referrerurl:
                item['parent'] = "Transfixed"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'wicked' in referrerurl:
                item['parent'] = "Wicked"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'zerotolerance' in referrerurl:
                item['parent'] = "Zero Tolerance"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))

            #  The following sites were brought in from other scrapers.  Date limits are to avoid dupes
            donotyield = 0
            if (('mypervyfamily' in item['url'] and item['date'] < "2021-10-06") or ('Filthy Blowjobs' in item['site'] and item['date'] < "2021-09-14") or ('Filthy Massage' in item['site'] and item['date'] < "2021-09-28") or ('Filthy Newbies' in item['site'] and item['date'] < "2021-09-21") or ('Filthy POV' in item['site'] and item['date'] < "2021-10-05") or ('Filthy Taboo' in item['site'] and item['date'] < "2021-10-09")):
                donotyield = 1

            if (('Lusty Grandmas' in item['site'] and item['date'] < "2019-02-01") or ('Grandpas Fuck Teens' in item['site'] and item['date'] < "2019-02-06") or ('Baby Got Balls' in item['site'] and item['date'] < "2008-05-04") or ('Creampie Reality' in item['site'] and item['date'] < "2006-10-04") or ('Cumming Matures' in item['site'] and item['date'] < "2009-12-01")):
                donotyield = 1

            if (('Dominated Girls' in item['site'] and item['date'] < "2013-08-26") or ('Home Porn Reality' in item['site'] and item['date'] < "2010-06-18") or ('Mandy Is Kinky' in item['site'] and item['date'] < "2008-04-30") or ('Mighty Mistress' in item['site'] and item['date'] < "2014-05-20") or ('Teach Me Fisting' in item['site'] and item['date'] < "2019-01-29") or ('Zoliboy' in item['site'] and item['date'] < "2018-03-18") or ('Pee And Blow' in item['site'] and item['date'] < "2009-12-16") or ('Speculum Plays' in item['site'] and item['date'] < "2007-09-07")):
                donotyield = 1

            #  Old Young Lesbian Love is returned both from Girlsway and 21Sextreme.  Only pull from Girlsway
            if "oldyounglesbianlove" in scene['sitename'] and "21sextreme" in referrerurl:
                donotyield = 1

            matches = ['dpfanatics', 'evilangelpartner', 'nudefightclub']
            if not any(x in scene['sitename'] for x in matches):
                if not donotyield:
                    days = int(self.days)
                    if days > 27375:
                        filterdate = "0000-00-00"
                    else:
                        filterdate = date.today() - timedelta(days)
                        filterdate = filterdate.strftime('%Y-%m-%d')

                    if self.debug:
                        if not item['date'] > filterdate:
                            item['filtered'] = "Scene filtered due to date restraint"
                        print(item)
                    else:
                        if filterdate:
                            if item['date'] > filterdate:
                                yield item
                        else:
                            yield item

    def call_algolia(self, page, token, referrer):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }
        if '21sextreme' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3A21sextreme%22%2C%22availableOnSite%3Alustygrandmas%22%2C%22availableOnSite%3Agrandpasfuckteens%22%2C%22availableOnSite%3Ababygotballs%22%2C%22availableOnSite%3Acreampiereality%22%2C%22availableOnSite%3Acummingmatures%22%2C%22availableOnSite%3Adominatedgirls%22%2C%22availableOnSite%3Ahomepornreality%22%2C%22availableOnSite%3Amandyiskinky%22%2C%22availableOnSite%3Amightymistress%22%2C%22availableOnSite%3Apeeandblow%22%2C%22availableOnSite%3Aspeculumplays%22%2C%22availableOnSite%3Ateachmefisting%22%2C%22availableOnSite%3Atransfrombrazil%22%2C%22availableOnSite%3Atranssmuts%22%2C%22availableOnSite%3Azoliboy%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if '21sextury' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3A21sextury%22%2C%22availableOnSite%3Aanalteenangels%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Aalettaoceanempire%22%2C%22availableOnSite%3Aassholefever%22%2C%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3Aanalqueenalysa%22%2C%22availableOnSite%3Ablueangellive%22%2C%22availableOnSite%3Abuttplays%22%2C%22availableOnSite%3Acheatingwhorewives%22%2C%22availableOnSite%3Aclubsandy%22%2C%22availableOnSite%3Acutiesgalore%22%2C%22availableOnSite%3Adeepthroatfrenzy%22%2C%22availableOnSite%3Agapeland%22%2C%22availableOnSite%3Ahotmilfclub%22%2C%22availableOnSite%3Aletsplaylez%22%2C%22availableOnSite%3Aonlyswallows%22%2C%22availableOnSite%3Apixandvideo%22%2C%22availableOnSite%3Asexwithkathianobili%22%2C%22availableOnSite%3Asweetsophiemoone%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3A21sextury%22%2C%22availableOnSite%3Aanalteenangels%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Aalettaoceanempire%22%2C%22availableOnSite%3Aassholefever%22%2C%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3Aanalqueenalysa%22%2C%22availableOnSite%3Ablueangellive%22%2C%22availableOnSite%3Abuttplays%22%2C%22availableOnSite%3Acheatingwhorewives%22%2C%22availableOnSite%3Aclubsandy%22%2C%22availableOnSite%3Acutiesgalore%22%2C%22availableOnSite%3Adeepthroatfrenzy%22%2C%22availableOnSite%3Agapeland%22%2C%22availableOnSite%3Ahotmilfclub%22%2C%22availableOnSite%3Aletsplaylez%22%2C%22availableOnSite%3Aonlyswallows%22%2C%22availableOnSite%3Apixandvideo%22%2C%22availableOnSite%3Asexwithkathianobili%22%2C%22availableOnSite%3Asweetsophiemoone%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if '21naturals' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3A21naturals%22%2C%22availableOnSite%3A21eroticanal%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'addicted2girls' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22studio_name%22%2C%22serie_name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22download_sizes%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'agentredgirl' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22content_tags%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22content_tags%3Atrans%22%5D%2C%5B%22availableOnSite%3Aagentredgirl%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_tags&facetFilters=%5B%5B%22availableOnSite%3Aagentredgirl%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22content_tags%3Atrans%22%5D%5D"}]}'
        if 'biphoria' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'evilangel' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=100&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Aevilangel%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20serie_name%3A%20%22Member%20Compilations%22%20AND%20NOT%20categories.name%3A%20%22EA%20Short%22%20AND%20NOT%20clip_id%3A%20181315&facets=%5B%22categories.name%22%2C%22directors.name%22%2C%22actors.name%22%2C%22serie_name%22%2C%22length_range_15min%22%2C%22download_sizes%22%2C%22bisex%22%2C%22shemale%22%2C%22upcoming%22%2C%22lesbian%22%5D&tagFilters=&facetFilters=%5B%5B%22lesbian%3A%22%5D%2C%5B%22upcoming%3A0%22%5D%2C%5B%22shemale%3A0%22%5D%2C%5B%22bisex%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Aevilangel%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20serie_name%3A%20%22Member%20Compilations%22%20AND%20NOT%20categories.name%3A%20%22EA%20Short%22%20AND%20NOT%20clip_id%3A%20181315&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=lesbian&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22shemale%3A0%22%5D%2C%5B%22bisex%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Aevilangel%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20serie_name%3A%20%22Member%20Compilations%22%20AND%20NOT%20categories.name%3A%20%22EA%20Short%22%20AND%20NOT%20clip_id%3A%20181315&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22lesbian%3A%22%5D%2C%5B%22shemale%3A0%22%5D%2C%5B%22bisex%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Aevilangel%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20serie_name%3A%20%22Member%20Compilations%22%20AND%20NOT%20categories.name%3A%20%22EA%20Short%22%20AND%20NOT%20clip_id%3A%20181315&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=shemale&facetFilters=%5B%5B%22lesbian%3A%22%5D%2C%5B%22upcoming%3A0%22%5D%2C%5B%22bisex%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Aevilangel%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20serie_name%3A%20%22Member%20Compilations%22%20AND%20NOT%20categories.name%3A%20%22EA%20Short%22%20AND%20NOT%20clip_id%3A%20181315&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=bisex&facetFilters=%5B%5B%22lesbian%3A%22%5D%2C%5B%22upcoming%3A0%22%5D%2C%5B%22shemale%3A0%22%5D%5D"}]}'
        if 'fantasymassage' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Anurumassage%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Asoapymassage%22%2C%22availableOnSite%3Amassage-parlor%22%2C%22availableOnSite%3Amilkingtable%22%2C%22availableOnSite%3Afantasymassage%22%2C%22availableOnSite%3Atrickyspa%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'devilsfilm' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Asquirtalicious%22%2C%22availableOnSite%3Ahairyundies%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Adevilsfilmparodies%22%2C%22availableOnSite%3Agivemeteens%22%2C%22availableOnSite%3Aoutofthefamily%22%2C%22availableOnSite%3Adevilsgangbangs%22%2C%22availableOnSite%3AJaneDoePictures%22%2C%22availableOnSite%3Adevilstgirls%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'diabolic' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adiabolic%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adiabolic%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&clickAnalytics=false&facets=upcoming"}]}'
        if 'filthykings' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afilthykings%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afilthykings%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'genderx' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Agenderx%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20site_id%3A428&facets=%5B%22categories.name%22%2C%22actors.name%22%2C%22serie_name%22%2C%22length_range_15min%22%2C%22download_sizes%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Agenderx%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20site_id%3A428&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'girlsway' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Awebyoung%22%2C%22availableOnSite%3Agirlsway%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlstryanal%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Asquirtinglesbian%22%2C%22availableOnSite%3Aoldyounglesbianlove%22%2C%22availableOnSite%3Agirlcore%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Alesbianrevenge%22%2C%22availableOnSite%3Amomsonmoms%22%2C%22availableOnSite%3Awheretheboysarent%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Awebyoung%22%2C%22availableOnSite%3Agirlsway%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlstryanal%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Asquirtinglesbian%22%2C%22availableOnSite%3Aoldyounglesbianlove%22%2C%22availableOnSite%3Agirlcore%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Alesbianrevenge%22%2C%22availableOnSite%3Amomsonmoms%22%2C%22availableOnSite%3Awheretheboysarent%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'isthisreal' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Atrickyspa%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlsunderarrest%22%2C%22availableOnSite%3Abethecuck%22%2C%22availableOnSite%3Asistertrick%22%2C%22availableOnSite%3Aisthisreal%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}'
        if 'modeltime' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Amodeltime%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Amodeltime%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'moderndaysins' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amoderndaysins%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Amoderndaysins%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amoderndaysins%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Amoderndaysins%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amoderndaysins%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'mommysgirl' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amommysgirl%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Amommysgirl%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amommysgirl%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Amommysgirl%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amommysgirl%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'mypervyfamily' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amypervyfamily%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Amypervyfamily%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'clubinfernodungeon' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22studio_name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22download_sizes%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'nextdoorstudios' in referrer:
            jbody = '{"requests":[{"indexName":"nextdoorstudios_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Anextdoorstudios%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A107%20AND%20NOT%20serie_name%3A%22Member%20Compilations%22&facets=%5B%22categories.name%22%2C%22actors.name%22%2C%22sitename%22%2C%22length_range_15min%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"nextdoorstudios_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Anextdoorstudios%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A107%20AND%20NOT%20serie_name%3A%22Member%20Compilations%22&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'puretaboo' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Apuretaboo%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Apuretaboo%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}'
        if 'tabooheat' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}'
        if 'touchmywife' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atouchmywife%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=true&facets=%5B%22categories.name%22%2C%22channels.id%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atouchmywife%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&clickAnalytics=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
        if 'transfixed' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22content_tags%22%2C%22upcoming%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22content_tags%3Atrans%22%5D%2C%5B%22availableOnSite%3AAburningangel%22%2C%22availableOnSite%3Apuretaboo%22%2C%22availableOnSite%3Atransfixed%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Amodeltime%22%2C%22availableOnSite%3ABeingTrans247%22%2C%22availableOnSite%3ATransgressiveFilms%22%5D%5D"},{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22content_tags%3Atrans%22%5D%2C%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Aburningangel%22%2C%22availableOnSite%3Apuretaboo%22%2C%22availableOnSite%3Atransfixed%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Amodeltime%22%2C%22availableOnSite%3ABeingTrans247%22%2C%22availableOnSite%3ATransgressiveFilms%22%5D%5D"},{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=content_tags&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Aburningangel%22%2C%22availableOnSite%3Apuretaboo%22%2C%22availableOnSite%3Atransfixed%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Amodeltime%22%2C%22availableOnSite%3ABeingTrans247%22%2C%22availableOnSite%3ATransgressiveFilms%22%5D%5D"},{"indexName":"all_scenes_rating_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22content_tags%3Atrans%22%5D%5D"}]}'
        if 'wicked' in referrer:
            jbody = '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Awicked%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A427%20AND%20NOT%20serie_name%3A%27Member%20Compilations%27&facets=%5B%22categories.name%22%2C%22directors.name%22%2C%22female_actors.name%22%2C%22serie_name%22%2C%22length_range_15min%22%2C%22download_sizes%22%2C%22genres.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Awicked%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A427%20AND%20NOT%20serie_name%3A%27Member%20Compilations%27&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}'
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
