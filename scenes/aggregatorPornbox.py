import json
import string
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class PornboxSingleSiteSpider(BaseSceneScraper):
    name = 'PornboxSingleSite'
    network = 'Pornbox'
    parent = 'Pornbox'

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    cookies = [
        {"name": "agree18", "value": "1"},
        {"name": "version_website_id", "value": "j:[25,1013,1401,1402]"},
    ]

    start_urls = [
        'https://pornbox.com/',
    ]

    studios = [
        # ~ {'studio': 6221, 'site': 'dannysteele'},
        # ~ {'studio': 8096, 'site': 'jmac'},
        # ~ {'studio': 4550, 'site': 'dollydyson'},
        # ~ {'studio': 35, 'site': 'interracialvision'},
        # ~ {'studio': 112, 'site': 'madelainerousset'},
        # ~ {'studio': 190, 'site': 'viragoldfilms'},
        # ~ {'studio': 305, 'site': 'erikakortistudio'},
        # ~ {'studio': 2127, 'site': 'erotichna'},
        # ~ {'studio': 560, 'site': 'steverickz'},
        # ~ {'studio': 462, 'site': 'maximogarcia'},
        # ~ {'studio': 474, 'site': 'nashidni'},
        # ~ {'studio': 347, 'site': 'madenasty'},
        # ~ {'studio': 4892, 'site': 'montecristoxv'},
        # ~ {'studio': 9271, 'site': 'asiaxxxtour'},
        # ~ {'studio': 270, 'site': 'stalkerprodz'},
        # ~ {'studio': 2800, 'site': 'leodee'},
        # ~ {'studio': 6438, 'site': 'murgang'},
        # ~ {'studio': 698, 'site': 'lancelotstyles'},
        # ~ {'studio': 12209, 'site': 'bukkakeorgy'},
        # ~ {'studio': 10714, 'site': 'WreccItRalph'},
        # ~ {'studio': 4344, 'site': 'filoufitt'},
        # ~ {'studio': 1547, 'site': 'novinhosdaimperium'},
        # ~ {'studio': 2320, 'site': 'arinafox'},
        # ~ {'studio': 111, 'site': 'yummyestudio'},
        # ~ {'studio': 2611, 'site': 'fuckingpornstars'},
        # ~ {'studio': 2976, 'site': 'martinspell'},
        # ~ {'studio': 1547, 'site': 'Novinhosdaimperium'},
        # ~ {'studio': 11257, 'site': 'Gaelbrandao'},
        # ~ {'studio': 2826, 'site': 'Daisymelanin00'},
        {'studio': 996, 'site': 'TedOficial'},
    ]

    content_json_url = 'https://pornbox.com/contents/%s'
    content_url = 'https://pornbox.com/application/watch-page/%s'

    selector_map = {
        'external_id': r'\/([0-9]+)',
        'pagination': 'studio/%s?skip=%s&sort=latest',
        'type': 'Scene',
    }

    def start_requests(self):
        for studio in self.studios:
            meta = {}
            meta['site'] = studio['site']
            meta['studio'] = studio['studio']
            meta['page'] = self.page

            countries = requests.get("https://pornbox.com/model/country", verify=False).content
            meta['countries'] = json.loads(countries)

            url = self.get_next_page_url('https://pornbox.com/', self.page, meta)

            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, meta):
        return self.format_url(base, self.get_selector_map('pagination') % (meta['studio'], page))

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        scenes = jsondata['contents']
        for scene in scenes:
            yield scrapy.Request(url=self.content_json_url % scene['id'],
                                 callback=self.parse_scene,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)

        item = SceneItem()

        item['title'] = string.capwords(jsondata['scene_name'])
        if "small_description" in jsondata and jsondata['small_description']:
            item['description'] = self.cleanup_description(jsondata['small_description'])
        else:
            item['description'] = ""
        item['site'] = response.meta['site']
        item['date'] = self.parse_date(jsondata['publish_date']).strftime('%Y-%m-%d')
        item['image'] = jsondata['player_poster']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = []
        item['performers_data'] = []
        if jsondata['models']:
            for model in jsondata['models']:
                item['performers'].append(string.capwords(model['model_name']))
                performer_extra = {}
                performer_extra['name'] = string.capwords(model['model_name'])
                performer_extra['site'] = "Legal Porno"
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = string.capwords(model['sex'])
                for country in meta['countries']:
                    if model['country_id'] == country['country_id']:
                        performer_extra['extra']['nationality'] = string.capwords(country['nationality'])
                        performer_extra['extra']['birthplace'] = string.capwords(country['name'])
                        performer_extra['extra']['birthplace_code'] = country['code']
                item['performers_data'].append(performer_extra)

        if jsondata['male_models']:
            for model in jsondata['male_models']:
                item['performers'].append(string.capwords(model['model_name']))
                performer_extra = {}
                performer_extra['name'] = string.capwords(model['model_name'])
                performer_extra['site'] = "Legal Porno"
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = string.capwords(model['sex'])
                for country in meta['countries']:
                    if model['country_id'] == country['country_id']:
                        performer_extra['extra']['nationality'] = string.capwords(country['nationality'])
                        performer_extra['extra']['birthplace'] = string.capwords(country['name'])
                        performer_extra['extra']['birthplace_code'] = country['code']
                item['performers_data'].append(performer_extra)

        item['tags'] = list(map(lambda tag: string.capwords(tag['niche'].strip()), jsondata['niches']))

        item['id'] = jsondata['id']
        item['duration'] = self.duration_to_seconds(jsondata['runtime'])

        item['url'] = self.content_url % jsondata['id']
        item['network'] = item['site']
        item['parent'] = item['site']
        item['type'] = 'Scene'

        for key in ['markers', 'trailer']:
            item[key] = ''

        yield self.check_item(item, self.days)
