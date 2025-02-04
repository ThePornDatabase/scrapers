import re
import string
import json
from datetime import date, timedelta
import unidecode
import scrapy

from tpdb.BaseMovieScraper import BaseMovieScraper
from tpdb.items import MovieItem


class MoviesTMDBSpider(BaseMovieScraper):
    name = 'TMDBMovies'
    network = 'TMDB'
    site = 'TMDB'

    start_urls = [
        'https://api.themoviedb.org',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/3/discover/movie?api_key=70c31dc13529fefc4a73fd47b13a4cef&language=en-US&sort_by=primary_release_date.desc&certification_country=US&certification.gte=NC-17&include_adult=true&include_video=false&page=%s&with_watch_monetization_types=flatrate'
    }

    def get_movies(self, response):
        jsondata = json.loads(response.text)
        for movie in jsondata['results']:
            if movie['adult']:
                link = f'https://api.themoviedb.org/3/movie/{movie["id"]}?api_key=70c31dc13529fefc4a73fd47b13a4cef&language=en-US&append_to_response=credits,genres,keywords,%20collections'
                yield scrapy.Request(link, callback=self.parse_movie)

    def parse_movie(self, response):
        jsondata = json.loads(response.text)
        item = MovieItem()
        item['id'] = jsondata['id']
        item['trailer'] = ''
        item['format'] = ''

        item['site'] = "TMDB"
        item['network'] = "TMDB"
        item['title'] = string.capwords(jsondata['title'])
        item['description'] = jsondata['overview']
        item['date'] = jsondata['release_date']
        if 'keywords' in jsondata['keywords']:
            item['tags'] = list(map(lambda x: string.capwords(x['name']), jsondata['keywords']['keywords']))

        item['performers'] = list(map(lambda x: unidecode.unidecode(string.capwords(x['name'])), jsondata['credits']['cast']))
        item['image_front'] = f"https://image.tmdb.org/t/p/original{jsondata['poster_path']}"
        # ~ item['image_front_blob'] = self.get_image_blob_from_link(item['image_front'])
        item['image_front_blob'] = None
        item['image_back'] = None
        item['image_back_blob'] = None

        item['url'] = f'https://www.themoviedb.org/movie/{item["id"]}'
        if len(jsondata['production_companies']):
            item['studio'] = unidecode.unidecode(string.capwords(jsondata['production_companies'][0]['name'])).strip()
        else:
            item['studio'] = None
        item['rating'] = None
        item['director'] = None
        for crew in jsondata['credits']['crew']:
            if "director" in crew['job'].lower():
                item['director'] = unidecode.unidecode(string.capwords(crew['name'])).strip()
        item['year'] = re.search(r'(\d{4})', item['date']).group(1)
        if jsondata['runtime']:
            item['length'] = str(jsondata['runtime'])
        else:
            item['length'] = None
        item['sku'] = str(jsondata['imdb_id'])
        item['upc'] = None

        if item['title']:
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
                        return item
                else:
                    return item
            return None

    def get_elastic_payload(self, per_page, offset: int = 0):
        return {"size": per_page, "from": offset, "sort": [{"releaseDate": {"order": "desc"}}, {"tracking.views.weekly": {"order": "desc", "nested_path": "tracking.views"}}], "query": {"bool": {"must": [{"match": {"status": "ok"}}, {"range": {"releaseDate": {"lte": "now"}}}], "must_not": [{"match": {"type": "trailer"}}]}}, "aggs": {"aggs": {"nested": {"path": "genres"}, "aggs": {"genres": {"terms": {"field": "genres.name.untouched", "size": 400}}}}}}
