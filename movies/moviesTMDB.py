import re
import os
import requests
import string
import json
from datetime import date, timedelta
import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MoviesTMDBSpider(BaseSceneScraper):
    name = 'TMDBMovies'

    # TMDB keys are issued per account, so this one is a personal credential and
    # must not live in the repo.  Export TMDB_API_KEY before running.
    api_key = os.environ.get('TMDB_API_KEY', '')

    start_urls = [
        'https://api.themoviedb.org',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': f'/3/discover/movie?api_key={api_key}&language=en-US&sort_by=primary_release_date.desc&certification_country=US&certification.gte=NC-17&include_adult=true&include_video=false&page=%s&with_watch_monetization_types=flatrate'
    }

    async def start(self):
        print("Hello! Starting TMDB Movie Scraper")
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print(f'My public IP address is: {ip}')

        meta = {'page': self.page}

        # --- 1. Load URLs from file ---
        filepath = r"c:\temp\request.txt"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        else:
            urls = []

        # If the file contained URLs, use them
        if urls:
            for url in urls:
                # Only handle themoviedb URLs
                if "themoviedb" not in url.lower():
                    continue

                # Extract the numeric ID prefix (same regex you already use)
                match = re.search(r'.*/(\d{3,10}-)', url)
                if not match:
                    continue

                movie_id = match.group(1)
                link = (
                    f"https://api.themoviedb.org/3/movie/{movie_id}"
                    f"?api_key={self.api_key}&language=en-US"
                    f"&append_to_response=credits,genres,keywords,%20collections"
                )

                yield scrapy.Request(
                    link,
                    callback=self.parse_movie,
                    headers=self.headers,
                    cookies=self.cookies
                )
            return  # <-- Done processing file-based URLs

        # --- 2. Fall back to existing behavior if no file URLs were found ---
        singleurl = self.settings.get('url')
        if singleurl:
            match = re.search(r'.*/(\d{3,10}-)', singleurl)
            if match:
                movie_id = match.group(1)
                link = (
                    f'https://api.themoviedb.org/3/movie/{movie_id}'
                    f'?api_key={self.api_key}&language=en-US'
                    f'&append_to_response=credits,genres,keywords,%20collections'
                )
                yield scrapy.Request(link, callback=self.parse_movie)
        else:
            for link in self.start_urls:
                yield scrapy.Request(
                    url=self.get_next_page_url(link, self.page),
                    callback=self.parse,
                    meta=meta,
                    headers=self.headers,
                    cookies=self.cookies
                )


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
        if not item['date'] or item['date'] == '0000-00-00':
            item['date'] = None
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
