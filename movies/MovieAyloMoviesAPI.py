import re
import string
from urllib.parse import urlencode
import datetime
import scrapy
import json
import requests
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieAyloAPISpider(BaseSceneScraper):
    name = 'MovieAyloAPI'
    network = 'Mind Geek'

    start_urls = [
        'https://www.biempire.com',
        'https://www.digitalplayground.com',
        'https://www.iconmale.com',
        'https://www.milehighmedia.com',
        'https://www.milfed.com',
        'https://www.noirmale.com',
        'https://www.transsensual.com',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False', 'CONCURRENT_REQUESTS': '4'}

    paginations = [
        '/movies?page=%s',
        # ~ '/series?page=%s'
    ]

    selector_map = {
        'external_id': '(\\d+)$',

    }

    def start_requests(self):
        meta = {}
        for url in self.start_urls:
            meta['url'] = url
            meta['firstpage'] = True
            meta['page'] = self.page - 1
            for pagination in self.paginations:
                meta['pagination'] = pagination
                yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies, meta=meta, dont_filter=True)

    def parse(self, response):
        meta = response.meta

        process_page = True
        if "firstpage" in meta and meta['firstpage']:
            meta['firstpage'] = False
        else:
            jsondata = response.json()
            if isinstance(jsondata, dict) and jsondata['result']:
                movies = self.get_movies(response)
                for movie in movies:
                    yield movie
            else:
                process_page = False

        if "token" in meta and meta['token']:
            token = meta['token']
        else:
            token = self.get_token(response)
            meta['token'] = token

        if process_page:
            meta['headers'] = {'instance': token}
            meta['limit'] = 25

            link = self.get_next_page(response, meta['pagination'])
            meta['page'] = meta['page'] + 1

            yield scrapy.Request(url=link, callback=self.parse, headers={'instance': token}, meta=meta, dont_filter=True)

    def get_movies(self, response):
        meta = response.meta
        for scene in response.json()['result']:
            item = SceneItem()
            # ~ print("Movie")
            # ~ print("----------------------------------")
            # ~ print(scene)
            # ~ print()
            # ~ print()
            item['trailer'] = self.get_trailer(scene)
            item['id'] = str(scene['id'])
            item['title'] = string.capwords(scene['title'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['dateReleased']).group(1)
            if scene['collections'] and len(scene['collections']):
                item['site'] = scene['collections'][0]['name']
            else:
                item['site'] = scene['brandMeta']['displayName']
            if "digitalplayground" in response.url:
                item['site'] = "Digital Playground"
            item['parent'] = scene['brandMeta']['displayName']

            if scene['brand'] == "milehigh":
                scene['brand'] = "milehighmedia"

            item['url'] = f"https://www.{scene['brand']}.com/movie/{scene['id']}/{slugify(item['title'])}"

            if not self.settings.get('force_update'):
                submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            else:
                submitmovie = True

            if "children" in scene:
                scenecount = len(scene['children'])
            else:
                scenecount = 99

            if submitmovie and scenecount > 1 and item['date']:

                if 'description' in scene:
                    item['description'] = scene['description']
                else:
                    item['description'] = ''

                item['performers'], item['performers_data'] = self.get_performers_data(scene['actors'], item['site'])

                item['tags'] = []
                for tag in scene['tags']:
                    item['tags'].append(tag['name'])

                # ~ item['scenes'] = []
                # ~ for child in scene['children']:
                    # ~ item['scenes'].append({'site': item['site'], 'external_id': str(child['id'])})

                item['network'] = self.network

                item['image'] = self.get_image(scene, "Movie")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['type'] = 'Movie'
                meta['movie'] = item.copy()

                if self.check_item(item, self.days):
                    item['scenes'] = []
                    response.meta['movie'] = item.copy()
                    for child in scene['children']:
                        if "type" in child and child['type'].lower() == "scene":
                            link = f"https://site-api.project1service.com/v2/releases/{child['id']}"
                            sceneitem = requests.get(link, headers=response.meta['headers'])
                            scenejson = json.loads(sceneitem.text)
                            if isinstance(scenejson, (list, dict)) and "result" in scenejson:
                                scenejson = scenejson['result']
                                sceneitem = self.parse_scene(scenejson, item)
                                item['scenes'].append({'site': sceneitem['site'], 'external_id': sceneitem['id']})
                                yield sceneitem
                    yield item

    def parse_scene(self, scene, movie):
        # ~ print("Scene")
        # ~ print("----------------------------------")
        # ~ print(scene)
        # ~ print()
        # ~ print()
        item = SceneItem()

        if len(scene['videos']):
            item['trailer'] = self.get_trailer(scene)
        else:
            item['trailer'] = ''

        item['id'] = str(scene['id'])
        item['title'] = string.capwords(scene['title'])
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['dateReleased']).group(1)
        if scene['collections'] and len(scene['collections']):
            item['site'] = scene['collections'][0]['name']
        else:
            item['site'] = scene['brandMeta']['displayName']
        if item['site'].lower() == "dpw":
            item['site'] = "DP World"
        item['parent'] = scene['brandMeta']['displayName']

        if scene['brand'] == "milehigh":
            scene['brand'] = "milehighmedia"

        item['url'] = f"https://www.{scene['brand']}.com/scene/{scene['id']}/{slugify(item['title'])}"

        if 'description' in scene:
            item['description'] = scene['description']
        else:
            item['description'] = ''

        item['performers'], item['performers_data'] = self.get_performers_data(scene['actors'], item['site'])

        item['tags'] = []
        for tag in scene['tags']:
            item['tags'].append(tag['name'])

        item['network'] = self.network
        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]

        item['image'] = self.get_image(scene, "Scene")
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['type'] = 'Scene'

        return item

    def get_next_page(self, response, pagination):
        meta = response.meta
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)

        if "movies" in pagination:
            releasetype = 'movie'
        if "series" in pagination:
            releasetype = 'serie'

        query = {
            'dateReleased': f"<{tomorrow}",
            'limit': meta['limit'],
            'offset': (meta['page'] * meta['limit']),
            'orderBy': '-dateReleased',
            'type': releasetype,
            'referrer': meta['url'],
            'blockName': 'MovieListBlock',
            'pageType': 'EXPLORE_MOVIES'
        }

        print('NEXT PAGE: ' + str(meta['page']))
        link = 'https://site-api.project1service.com/v2/releases?' + urlencode(query)
        return link

    def get_token(self, response):
        token = re.search('instance_token=(.+?);', response.headers.getlist('Set-Cookie')[0].decode("utf-8"))
        return token.group(1)

    def get_image(self, scene, imagetype):
        image_arr = []
        if imagetype == "Scene":
            if 'card_main_rect' in scene['images'] and len(scene['images']['card_main_rect']):
                image_arr = scene['images']['card_main_rect']
            elif 'poster' in scene['images'] and len(scene['images']['poster']):
                image_arr = scene['images']['poster']
        else:
            if 'cover' in scene['images'] and len(scene['images']['cover']):
                image_arr = scene['images']['cover']
            elif 'card_main_rect' in scene['images'] and len(scene['images']['card_main_rect']):
                image_arr = scene['images']['card_main_rect']
            elif 'poster' in scene['images'] and len(scene['images']['poster']):
                image_arr = scene['images']['poster']

        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        for index in image_arr:
            image = image_arr[index]
            for size in sizes:
                if size in image:
                    return image[size]['url']

    def get_trailer(self, scene):
        for index in scene['videos']:
            trailer = scene['videos'][index]
            for size in ['720p', '576p', '480p', '360p', '320p', '1080p', '4k']:
                if size in trailer['files']:
                    return trailer['files'][size]['urls']['view']

    def get_performers_data(self, performers, site):
        performers_data = []
        performers = []
        print(performers)
        if len(performers):
            for performer in performers:
                performers.append(performer['name'])
                perf = {}
                perf['name'] = performer['name']
                perf['extra'] = {}
                if "gender" in performer and performer['gender']:
                    if performer['gender'].lower() == "trans":
                        performer['gender'] = "Transgender Female"
                    perf['extra']['gender'] = string.capwords(performer['gender'])
                    perf['network'] = self.network
                    perf['site'] = site
                    performers_data.append(perf)
        print(performers, performers_data)
        return performers, performers_data
