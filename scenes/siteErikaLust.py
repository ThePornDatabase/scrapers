import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class SiteErikaLustSpider(BaseSceneScraper):
    name = 'ErikaLust'
    network = 'ErikaLust'
    parent = 'ErikaLust'
    site = 'ErikaLust'

    start_urls = [
        'https://erikalust.com/api/movies/filtered?page=1&sortBy=default&direction=desc&optimized=1&is-original=1',
    ]

    cookies = [{"name": "age_restriction", "value": true}]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'image_blob': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/api/movies/filtered?page=%s&sortBy=default&direction=desc&optimized=1&is-original=1',
        #'pagination': '/api/movies/filtered?page=%s&sortBy=default&direction=desc',
        'type': 'Scene',
    }

    async def start(self):
        link = "https://erikalust.com/film?originals=true&order=default"
        yield scrapy.Request(link, callback=self.start_requests_2, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = {}
        responsetext = response.text
        responsetext = responsetext.replace("\n", "").replace("\r", "").replace("\t", "").strip()
        token = re.search(r'Bearer.*?access_token=[\'\"](.*?)[\'\"]', responsetext)
        if token:
            meta['token'] = token.group(1)

            ip = requests.get('https://api.ipify.org').content.decode('utf8')
            print('My public IP address is: {}'.format(ip))

            meta['page'] = self.page

            for link in self.start_urls:
                meta['headers'] = {"Authorization": f"Bearer {meta['token']}"}
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=meta['headers'], cookies=self.cookies)
        else:
            print("No token found.  Aborting")

    def parse(self, response, **kwargs):
        movies = self.get_films(response)
        count = 0
        for movie in movies:
            count += 1
            yield movie

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response, page=response.meta['page'] + 1)
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, headers=meta['headers'], meta=meta)

    def get_films(self, response):
        meta = self.copy_meta(response)
        filmsjson = response.json()
        filmsjson = filmsjson['data']
        for film in filmsjson:
            meta['movie'] = film['title']
            meta['slug'] = film['slug']
            meta['id'] = film['id']
            if 'poster_picture' in film and film['poster_picture']:
                meta['series_cover'] = film['poster_picture']
                if meta['series_cover'] and "?" in meta['series_cover']:
                    meta['series_cover'] = re.search(r'(.*?)\?', meta['series_cover']).group(1)
                meta['series_cover_blob'] = self.get_image_blob_from_link(meta['series_cover'])
            filmurl = f"https://erikalust.com/api/movies/{meta['id']}"
            yield scrapy.Request(filmurl, callback=self.get_scenes, headers=meta['headers'], meta=meta)
           
    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenejson = response.json()
        scene= scenejson['data']

        item = SceneItem()
        item['id'] = scene['id']
        item['title'] = scene['title']
        if "title" in scenejson and scenejson['title']:
            titletext = f"{scenejson['title']}:   "
        else:
            titletext = ""
        item['description'] = self.cleanup_description(scene['synopsis_clean'])
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['release_date']).group(1)
        item['duration'] = self.duration_to_seconds(scene['length'])
        item['image'] = scene['poster_picture']
        if item['image'] and "?" in item['image']:
            item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        if meta['series_cover']:
            item['back'] = meta['series_cover']
            item['back_blob'] = meta['series_cover_blob']
        item['tags'] = []
        for tag in scene['labels']:
            item['tags'].append(tag['name'])
            
        if scene['confession']:
            item['site'] = "xConfessions"
        else:
            item['site'] = "LustCinema"
        item['parent'] = "Erika Lust"
        item['network'] = "Erika Lust"
        
        item['performers'] = []
        #item['performers_data'] = []
        for performer in scene['performers']:
            performer_data = {}
            performer_data_extra = {}
            performer_name = performer['name'] + " " + performer['last_name']
        
            performer_data['name'] = performer_name
            performer_data['image'] = performer['poster_image']
            performer_data['image_blob'] = self.get_image_blob_from_link(performer['poster_image'])
            performer_data['network'] = item['network']
            performer_data['site'] = item['site']
            performer_data_extra['gender'] = 'Male' if performer['gender'] == 0 else ('Female' if performer['gender'] == 1 else ('Non Binary' if performer['gender'] == 2 else ''))
            performer_data['extra']=[]
            performer_data['extra'].append(performer_data_extra)
            item['performers'].append(performer_name)
        #    item['performers'].append(performer_data)
        #    item['performers_data'].append(performer_data)

        item['trailer'] = f"https://erikalust.com/film/watch/trailer/{scene['id']}"
        item['url'] = f"https://erikalust.com/film/{scene['id']}"
        
        
        if "director" in scene and scene['director']:
            director = scene['director']['name'] + " " + scene['director']['last_name']
            item['director'] = director.replace("Director", "").strip()
            
        item['markers'] = []
        if 'scene_markers' in scene:
            if scene['scene_markers']:
                for timetag in scene['scene_markers']:
                    timestamp = {}
                    timestamp['name'] = self.cleanup_title(timetag['name'])
                    timestamp['start'] = str(int(timetag['time']/1000))
                    item['markers'].append(timestamp)
                    item['tags'].append(timestamp['name'])

        yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image:
            # ~ header_list = response.request.headers.to_unicode_dict()
            # ~ headers = {'Authorization': header_list['Authorization']}
            req = requests.get(image, verify=True)

            # ~ req = Http.get(image, headers=response.headers, cookies=self.cookies, verify=False)
            if req and req.ok:
                return req.content
        return None
