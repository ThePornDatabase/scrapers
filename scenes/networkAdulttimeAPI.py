import re
import json
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

#  NOTE!   This scraper _ONLY_ pulls scenes from AdultTime sites with publicly available video index pages.
#          It will not pull any scenes or images that are unavailable if you simply go to the specific site
#          as a guest user in an incognito browser


def match_site(argument):
    match = {
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
    return match.get(argument, argument)


class AdultTimeAPISpider(BaseSceneScraper):
    name = 'AdulttimeAPI'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://www.21sextury.com',
        'https://www.clubinfernodungeon.com',
        'https://www.evilangel.com',
        'https://www.genderx.com',
        'https://www.girlsway.com',
        'https://www.modeltime.com',
        'https://www.nextdoorstudios.com',
        'https://www.puretaboo.com',
        'https://www.transfixed.com',
        'https://www.wicked.com',
        'https://www.zerotolerance.com',
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
        referrer_url = response.meta["url"]
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
                date = "1970-01-01"
                item['date'] = dateparser.parse(date).isoformat()
            item['performers'] = list(
                map(lambda x: x['name'], scene['actors']))
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))

            item['site'] = scene['sitename']
            item['site'] = match_site(item['site'])
            item['network'] = self.network

            if '21sextury' in referrer_url:
                item['parent'] = "21Sextury"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'clubinfernodungeon' in referrer_url:
                item['parent'] = "Club Inferno Dungeon"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'evilangel' in referrer_url:
                item['parent'] = "Evil Angel"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'genderx' in referrer_url:
                item['parent'] = "Gender X"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'girlsway' in referrer_url:
                item['parent'] = "Girlsway"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'modeltime' in referrer_url:
                item['parent'] = "Model Time"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'nextdoorstudios' in referrer_url:
                item['parent'] = "Next Door Studios"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'puretaboo' in referrer_url:
                item['parent'] = "Pure Taboo"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'transfixed' in referrer_url:
                item['parent'] = "Transfixed"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'wicked' in referrer_url:
                item['parent'] = "Wicked"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['url_title'] + '/' + str(scene['clip_id']))
            if 'zerotolerance' in referrer_url:
                item['parent'] = "Zero Tolerance"
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))

            matches = ['dpfanatics', 'evilangelpartner', 'mommysgirl', 'nudefightclub']
            if not any(x in item['site'] for x in matches):
                yield item

    def call_algolia(self, page, token, referrer):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page),
        }

        body = {
            'requests': [
                {
                    'indexName': 'all_scenes',
                    'params': 'filters=upcoming=0',
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
