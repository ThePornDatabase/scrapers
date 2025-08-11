import re
import requests
import string
import json
from datetime import date, timedelta
import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MoviesTMDBSpider(BaseSceneScraper):
    name = 'TMDBMovies'

    api_key = "f83c77e92929bd569b110e2ce4e86b7e"

    start_urls = [
        'https://api.themoviedb.org',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': f'/3/discover/movie?api_key={api_key}&language=en-US&sort_by=primary_release_date.desc&certification_country=US&certification.gte=NC-17&include_adult=true&include_video=false&page=%s&with_watch_monetization_types=flatrate'
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        singleurl = self.settings.get('url')
        if singleurl:
            singleurl = re.search(r'.*/(\d{3,10}-)', singleurl)
            if singleurl:
                singleurl = singleurl.group(1)
                link = f'https://api.themoviedb.org/3/movie/{singleurl}?api_key={self.api_key}&language=en-US&append_to_response=credits,genres,keywords,%20collections'
                yield scrapy.Request(link, callback=self.parse_movie)
        else:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        jsondata = json.loads(response.text)
        for movie in jsondata['results']:
            if movie['adult']:
                link = f'https://api.themoviedb.org/3/movie/{movie["id"]}?api_key={self.api_key}&language=en-US&append_to_response=credits,genres,keywords,%20collections'
                yield scrapy.Request(link, callback=self.parse_movie)

    def parse_movie(self, response):
        jsondata = json.loads(response.text)
        item = self.init_scene()
        item['id'] = jsondata['id']
        item['trailer'] = ''
        item['format'] = ''

        item['title'] = string.capwords(jsondata['title'])
        item['description'] = jsondata['overview']
        item['date'] = jsondata['release_date']
        if 'keywords' in jsondata['keywords']:
            item['tags'] = list(map(lambda x: string.capwords(x['name']), jsondata['keywords']['keywords']))

        item['performers'] = list(map(lambda x: unidecode.unidecode(string.capwords(x['name'])), jsondata['credits']['cast']))
        item['image'] = f"https://image.tmdb.org/t/p/original{jsondata['poster_path']}"
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['back'] = None
        item['back_blob'] = None

        item['url'] = f'https://www.themoviedb.org/movie/{item["id"]}'
        if len(jsondata['production_companies']):
            item['site'] = unidecode.unidecode(string.capwords(jsondata['production_companies'][0]['name'])).strip()
        else:
            item['site'] = "TMDB"
        item['parent'] = item['site']
        item['network'] = item['site']

        item['director'] = None
        for crew in jsondata['credits']['crew']:
            if "director" in crew['job'].lower():
                item['director'] = unidecode.unidecode(string.capwords(crew['name'])).strip()
        if jsondata['runtime']:
            item['duration'] = str(jsondata['runtime'])
        else:
            item['duration'] = None
        item['type'] = "Movie"

        yield self.check_item(item, self.days)

    def get_elastic_payload(self, per_page, offset: int = 0):
        return {"size": per_page, "from": offset, "sort": [{"releaseDate": {"order": "desc"}}, {"tracking.views.weekly": {"order": "desc", "nested_path": "tracking.views"}}], "query": {"bool": {"must": [{"match": {"status": "ok"}}, {"range": {"releaseDate": {"lte": "now"}}}], "must_not": [{"match": {"type": "trailer"}}]}}, "aggs": {"aggs": {"nested": {"path": "genres"}, "aggs": {"genres": {"terms": {"field": "genres.name.untouched", "size": 400}}}}}}
