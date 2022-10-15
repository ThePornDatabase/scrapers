import re
import base64
import string
import json
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MoviesBangSpider(BaseSceneScraper):
    name = 'BangMovies'
    network = 'Bang'
    parent = 'Bang'
    store = 'Bang'

    selector_map = {
        'external_id': 'video/(.+)'
    }

    per_page = 10

    def start_requests(self):
        if self.page:
            page = int(self.page)
        else:
            page = 0

        yield scrapy.Request(
            url='https://www.bang.com/api/search/dvds/dvd/_search',
            method='POST',
            headers={'Content-Type': 'application/json'},
            meta={'page': page},
            callback=self.parse,
            body=json.dumps(self.get_elastic_payload(self.per_page, 0))
        )

    def parse(self, response, **kwargs):
        movies = response.json()['hits']['hits']
        movies = self.parse_movie_internal(movies)
        count = 0
        for movie in movies:
            count += 1
            yield movie

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            next_page = response.meta['page'] + 1
            if (next_page * self.per_page) > response.json()['hits']['total']:
                return

            print('NEXT PAGE: ' + str(next_page))
            yield scrapy.Request(url='https://www.bang.com/api/search/dvds/dvd/_search', method='POST', headers={'Content-Type': 'application/json'}, callback=self.parse, meta={'page': next_page}, body=json.dumps(self.get_elastic_payload(self.per_page, self.per_page * next_page)))

    def parse_movie_internal(self, jsondata):
        # ~ print(jsondata)
        for movie in jsondata:
            # ~ print(f'JSON: {movie}')
            item = SceneItem()
            item['format'] = string.capwords(movie['_type'])
            if "dvd" not in item['format'].lower():
                print(f'Type: {item["format"]}')
            movie = movie['_source']
            # ~ print ("   ")
            item['id'] = movie['id']
            item['trailer'] = ''

            item['parent'] = string.capwords(movie['studio']['name'])
            item['site'] = string.capwords(movie['studio']['name'])
            item['store'] = self.store
            item['network'] = self.store
            item['title'] = string.capwords(movie['name'])
            item['description'] = movie['description']
            item['date'] = movie['releaseDate']
            item['tags'] = list(map(lambda x: string.capwords(x['name']), movie['genres']))
            item['performers'] = []
            item['performers'] = list(map(lambda x: string.capwords(x['name']), movie['actors']))
            item['image'] = f'https://i.bang.com/covers/{movie["identifier"]}/front.jpg'
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['back'] = f'https://i.bang.com/covers/{movie["identifier"]}/back.jpg'
            item['back_blob'] = self.get_image_blob_from_link(item['back'])
            if not item['back_blob']:
                item['back'] = None

            encode_url = self.encode_url(movie['id'])
            item['url'] = f'https://www.bang.com/dvd/{encode_url}'

            item['director'] = None
            item['duration'] = None
            item['sku'] = str(movie['identifier'])
            item['type'] = 'Movie'

            movie_query = '{"sort":[{"order":{"order":"asc"}}],"query": {"bool": {"must": [{"match": {"status": "ok"}}, {"nested": {"path": "dvd", "query": {"bool": {"must": [{"match": {"dvd.mongoId": {"query": "' + item['id'] + '", "operator": "AND"}}} ]}}}} ], "must_not": [{"match": {"type": "trailer"}} ]}}}'
            # ~ print(movie_query)
            yield scrapy.Request(url='https://www.bang.com/api/search/videos/video/_search', method='POST', headers={'Content-Type': 'application/json'}, meta={'item': item}, callback=self.parse_scenes, body=movie_query)

    def parse_scenes(self, response):
        item = response.meta['item']
        item['markers'] = []
        duration = 0
        movies = response.json()['hits']['hits']
        for movie in movies:
            movie = movie['_source']
            if "actions" in movie:
                for timetag in movie['actions']:
                    timestamp = {}
                    timestamp['name'] = self.cleanup_title(timetag['name'])
                    timestamp['start'] = str(int(timetag['timestamp']) + duration)
                    timestamp['end'] = None
                    item['markers'].append(timestamp)
                    item['tags'].append(timestamp['name'])
            if "genres" in movie:
                for genre in movie['genres']:
                    item['tags'].append(genre['name'])
            duration = duration + int(movie['duration'])
        item['duration'] = str(duration)
        item['tags'] = list(map(lambda x: string.capwords(x.strip()), list(set(item['tags']))))
        if item['title'] and 'dvd' in item['format'].lower():
            yield self.check_item(item, self.days)

    def get_elastic_payload(self, per_page, offset: int = 0):
        return {"size": per_page, "from": offset, "sort": [{"releaseDate": {"order": "desc"}}, {"tracking.views.weekly": {"order": "desc", "nested_path": "tracking.views"}}], "query": {"bool": {"must": [{"match": {"status": "ok"}}, {"range": {"releaseDate": {"lte": "now"}}}], "must_not": [{"match": {"type": "trailer"}}]}}, "aggs": {"aggs": {"nested": {"path": "genres"}, "aggs": {"genres": {"terms": {"field": "genres.name.untouched", "size": 400}}}}}}

    def encode_url(self, data):
        data = bytes.fromhex(data)
        data = base64.b64encode(data).decode('UTF-8')
        data = data.replace('+', '-').replace('/', '_').replace('=', ',')
        return data
