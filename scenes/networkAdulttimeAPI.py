import re
import json
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

#  NOTE!   This scraper _ONLY_ pulls scenes from AdultTime sites with publicly available video index pages.
#          It will not pull any scenes or images that are unavailable if you simply go to the specific site
#          as a guest user in an incognito browser


class AdultTimeAPISpider(BaseSceneScraper):
    name = 'AdultTimeAPI'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://freetour.adulttime.com/en/login',
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
        'external_id': '',
    }

    sitelist = {
        '21sextury': '21Sextury',
        'adulttime': 'AdultTime',
        'alettaoceanempire': 'Aletta Ocean Empire',
        'allgirlmassage': 'All Girl Massage',
        'analqueenalysa': 'Anal Queen Alysa',
        'analteenangels': 'Anal Teen Angels',
        'assholefever': 'Asshole Fever',
        'austinwilde': 'Austin Wilde',
        'blueangellive': 'Blue Angel Live',
        'burningangel': 'Burning Angel',
        'buttplays': 'Buttplays',
        'cheatingwhorewives': 'Cheating Whore Wives',
        'clubinfernodungeon': 'Club Inferno Dungeon',
        'clubsandy': 'Club Sandy',
        'codycummings': 'Cody Cummings',
        'cutiesgalore': 'Cuties Galore',
        'deepthroatfrenzy': 'Deepthroat Frenzy',
        'devilsfilm': 'Devils Film',
        'devilstgirls': 'Devils T-Girls',
        # 'dpfanatics': 'DPFanatics', Pulled from Gamma
        'evilangel': 'Evil Angel',
        'femalesubmission': 'Female Submission',
        'footsiebabes': 'Footsie Babes',
        'gapeland': 'Gapeland',
        'genderx': 'Gender X',
        'girlcore': 'Girlcore',
        'girlstryanal': 'Girls Try Anal',
        'girlsway': 'Girlsway',
        'hotmilfclub': 'Hot MILF Club',
        'lesbianfactor': 'Lesbian Factor',
        'letsplaylez': 'Lets Play Lez',
        'lezcuties': 'Lez Cuties',
        'marcusmojo': 'Marcus Mojo',
        'masonwyler': 'Mason Wyler',
        'modeltime': 'Model Time',
        # 'mommysgirl': 'Mommys Girl', Pulled from Gamma
        'momsonmoms': 'Moms on Moms',
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
        'oldyounglesbianlove': 'Old Young Lesbian Love',
        'oralexperiment': 'Oral Experiment',
        'pixandvideo': 'Pix And Video',
        'puretaboo': 'Pure Taboo',
        'roddaily': 'Rod Daily',
        'samuelotoole': 'Samuel Otoole',
        'sextapelesbians': 'Sextape Lesbians',
        'sexwithkathianobili': 'Sex With Kathia Nobili',
        'stagcollectivesolos': 'Stag Collective Solos',
        'strokethatdick': 'Stroke That Dick',
        'sweetsophiemoone': 'Sweet Sophie Moon',
        'tommydxxx': 'Tommy D XXX',
        'transfixed': 'Transfixed',
        'TransgressiveFilms': 'Transgressive Films',
        'truelesbian.com': 'TrueLesbian.com',
        'trystanbull': 'Trystan Bull',
        'webyoung': 'Web Young',
        'welikegirls': 'We Like Girls',
        'wheretheboysarent': 'Where the Boys Arent',
        'wicked': 'Wicked',
        'zerotolerance': 'Zero Tolerance',
    }

    excludes_list = ['dpfanatics', 'evilangelpartner', 'mommysgirl', 'nudefightclub']

    sites = ''
    excludes = ''

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        self.sites = ' OR '.join(['sitename:"%s"' % key for key in self.sitelist])
        self.excludes = ' OR NOT'.join(['sitename:"%s"' % key for key in self.excludes_list])

        for link in self.start_urls:
            yield scrapy.Request(url=link, callback=self.parse_token,
                                 meta={'page': 0, 'url': link})

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia(0, token, response.meta['url'], self.sites, self.excludes)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                next_page = response.meta['page'] + 1
                yield self.call_algolia(next_page, response.meta['token'], response.meta['url'], self.sites, self.excludes)

    def get_scenes(self, response):
        # ~ print(response.json()['results'])
        for scene in response.json()['results'][0]['hits']:
            item = SceneItem()

            item['image'] = ''
            for size in self.image_sizes:
                if size in scene['pictures']:
                    item['image'] = 'https://images-fame.gammacdn.com/movies' + \
                                    scene['pictures'][size]
                    break

            item['trailer'] = ''
            for size in self.trailer_sizes:
                if size in scene['trailers']:
                    item['trailer'] = scene['trailers'][size]
                    break

            item['id'] = scene['clip_id']

            if 'title' in scene and scene['title']:
                item['title'] = scene['title']
            else:
                item['title'] = scene['movie_title']

            item['description'] = scene['description']
            if dateparser.parse(scene['release_date']):
                item['date'] = dateparser.parse(scene['release_date']).isoformat()
            else:
                date = '1970-01-01'
                item['date'] = dateparser.parse(date).isoformat()

            item['performers'] = list(map(lambda x: x['name'], scene['actors']))
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))

            item['site'] = self.sitelist[scene['sitename']] if scene['sitename'] in self.sitelist else scene['sitename']
            item['network'] = self.network
            item['parent'] = scene['studio_name']
            item['url'] = None

            yield item

    def call_algolia(self, page, token, referrer, sites, excludes):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        headers = {
            'Content-Type': 'application/json',
            'Referer': referrer,
        }

        body = {
            'requests': [
                {
                    'indexName': 'all_scenes',
                    'params': 'filters=upcoming=0 AND (%s) AND (NOT %s)' % (sites, excludes),
                    'page': page,
                    'hitsPerPage': 100
                }
            ]
        }

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=json.dumps(body),
            meta={'token': token, 'page': page, 'url': referrer},
            callback=self.parse,
            headers=headers
        )
