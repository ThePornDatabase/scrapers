import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

# NOTE!   This scraper _ONLY_ pulls scenes from AdultTime sites with publicly available video index pages.
#         It will not pull any scenes or images that are unavailable if you simply go to the specific site
#         as a guest user in an incognito browser


def match_site(argument):
    match = {
        'wicked': 'Wicked',
        'evilangel': 'Evil Angel',
    }
    return match.get(argument.lower(), argument)


class AdultTimeMoviesAPISpider(BaseSceneScraper):
    name = 'AdulttimeMoviesAPI'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://www.evilangel.com',
        # ~ 'https://www.wicked.com',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False', 'CONCURRENT_REQUESTS': '2'}

    image_sizes = [
        '1920x1080',
        '1280x720',
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
        'pagination': '/en/movies/page/%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')
        page = int(self.page) - 1

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page + 1), callback=self.parse_token, meta={'page': page, 'url': link})

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia_movie(response.meta['page'], token, response.meta['url'])

    def parse(self, response, **kwargs):
        meta = response.meta
        if response.status == 200:
            movies = self.get_movies(response)
            # ~ print(f"Movies Len: {len(list(movies))}")
            count = 0
            for movie in movies:
                if movie is not None:
                    count += 1
                    # ~ scenecall = self.call_algolia_scene(meta['token'], meta["url"], movie['id'])
                    # ~ meta['movie'] = movie
                    # ~ yield scrapy.Request(url=scenecall['url'], method='post', body=scenecall['jbody'], meta=meta, callback=self.get_scenes, headers=scenecall['headers'])
                    yield movie

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    next_page = response.meta['page'] + 1
                    yield self.call_algolia_movie(next_page, response.meta['token'], response.meta['url'])

    def get_movies(self, response):
        meta = response.meta
        for scene in response.json()['results'][0]['hits']:
            # ~ print(scene)
            item = SceneItem()

            item['image'] = ''
            if scene['cover_path']:
                item['image'] = f"https://images02-openlife.gammacdn.com/movies/{scene['cover_path']}_front_400x625.jpg"
                item['image'] = item['image'].replace("movies//", "movies/")

            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = ''

            item['trailer'] = ''
            for size in self.trailer_sizes:
                if size in scene['trailers']:
                    item['trailer'] = scene['trailers'][size]
                    break

            item['id'] = scene['objectID'].split('-')[0]
            item['title'] = string.capwords(scene['title'])

            if 'description' in scene:
                item['description'] = scene['description']
            elif 'description' in scene['_highlightResult']:
                item['description'] = scene['_highlightResult']['description']['value']
            if 'description' not in item:
                item['description'] = ''

            if self.parse_date(scene['last_modified']):
                item['date'] = self.parse_date(scene['last_modified']).isoformat()
            else:
                item['date'] = self.parse_date(scene['date_created']).isoformat()

            item['performers'] = list(
                map(lambda x: x['name'], scene['actors']))
            if "directors" in scene:
                if scene['directors']:
                    item['director'] = scene['directors'][0]['name']
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))
            item['scenes'] = []
            item['duration'] = self.duration_to_seconds(scene['total_length'])
            item['sku'] = scene['objectID']
            item['network'] = self.network

            if "wicked" in meta['url']:
                item['site'] = scene['sitename_pretty']
                item['parent'] = scene['studio_name']
                item['url'] = f"https://www.wicked.com/en/movie/{scene['url_title']}/{item['id']}"

            if "evilangel" in meta['url']:
                item['site'] = "Evil Angel"
                item['parent'] = "Evil Angel"
                item['url'] = f"https://www.evilangel.com/en/movie/{scene['url_title']}/{item['id']}"

            item['type'] = 'Movie'

            # ~ print(item['title'], item['id'])
            yield self.check_item(item, self.days)

    def get_scenes(self, response):
        meta = response.meta
        movie = response.meta['movie']
        for scene in response.json()['results'][0]['hits']:
            item = SceneItem()

            item['image'] = ''
            for size in self.image_sizes:
                if size in scene['pictures']:
                    item['image'] = 'https://images-fame.gammacdn.com/movies' + \
                                    scene['pictures'][size]
                    break

            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = None

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

            item['title'] = string.capwords(item['title'])

            if 'description' in scene:
                item['description'] = scene['description']
            elif 'description' in scene['_highlightResult']:
                item['description'] = scene['_highlightResult']['description']['value']
            if 'description' not in item:
                item['description'] = ''
            if "director" in movie:
                item['director'] = movie['director']

            if self.parse_date(scene['release_date']):
                item['date'] = self.parse_date(scene['release_date']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = list(
                map(lambda x: x['name'], scene['actors']))
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))

            item['duration'] = scene['length']

            item['site'] = scene['sitename_pretty']
            item['parent'] = scene['studio_name']
            item['network'] = self.network
            movie['scenes'].append({'site': item['site'], 'external_id': item['id']})

            if "wicked" in meta['url']:
                item['url'] = f"https://www.wicked.com/en/video/{scene['url_title']}/{item['id']}"

            if "evilangel" in meta['url']:
                item['url'] = f"https://www.evilangel.com/en/video/evilangel/{scene['url_title']}/{item['id']}"

            item['type'] = 'Scene'

            yield item
        yield movie

    def call_algolia_movie(self, page, token, referrer):
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }

        if 'wicked' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=30&maxValuesPerFacet=10&page=' + str(page) + '&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Awicked%22%2C%22availableOnSite%3Awickedpartners%22%5D%5D"}]}'

        if 'evilangel' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aevilangel%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%5D"}]}'

        return scrapy.Request(url=algolia_url, method='post', body=jbody, meta={'token': token, 'page': page, 'url': referrer}, callback=self.parse, headers=headers)

    def call_algolia_scene(self, token, referrer, movie):
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token
        headers = {
            'Content-Type': 'application/json',
            'Referer': referrer
        }

        jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&page=0&facets=%5B%5D&tagFilters=&facetFilters=%5B%22movie_id%3A' + movie + '%22%5D"}]}'


        call_return = {}
        call_return['url'] = algolia_url
        call_return['jbody'] = jbody
        call_return['headers'] = headers
        return call_return
