import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieAdultTimeAPISpider(BaseSceneScraper):
    name = 'MovieAdulttimeAPI'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://www.allblackx.com',
        'https://www.biphoria.com',
        'https://www.bskow.com',
        'https://www.clubinfernodungeon.com',
        'https://www.darkx.com',
        'https://www.devilsfilm.com',
        'https://www.eroticax.com',
        'https://www.evilangel.com',
        'https://www.falconstudios.com',
        'https://www.fistingcentral.com',
        'https://www.genderxfilms.com',
        'https://www.girlfriendsfilms.com',
        'https://www.hardx.com',
        'https://www.lesbianx.com',
        'https://www.lethalhardcore.com',
        'https://www.peternorth.com',
        'https://www.ragingstallion.com',
        'https://www.roccosiffredi.com',
        'https://www.whiteghetto.com',
        'https://www.wicked.com',
        'https://www.zerotolerancefilms.com',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False', 'CONCURRENT_REQUESTS': '4'}

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
                    scenecall = self.call_algolia_scene(meta['token'], meta["url"], movie['id'])
                    meta['movie'] = movie
                    yield scrapy.Request(url=scenecall['url'], method='post', body=scenecall['jbody'], meta=meta, callback=self.get_scenes, headers=scenecall['headers'])
                    # ~ yield movie

            if 'page' in response.meta and response.meta['page'] < self.limit_pages and response.meta['page'] < 100:
                next_page = response.meta['page'] + 1
                print(f"*** Pulling Next Page: {next_page}")
                yield self.call_algolia_movie(next_page, response.meta['token'], response.meta['url'])

    def get_movies(self, response):
        meta = response.meta
        for scene in response.json()['results'][0]['hits']:
            # ~ print(scene)
            item = SceneItem()

            item['trailer'] = ''
            if "trailers" in scene:
                for size in self.trailer_sizes:
                    if size in scene['trailers']:
                        item['trailer'] = scene['trailers'][size]
                        break

            item['id'] = scene['objectID'].split('-')[0]
            item['title'] = string.capwords(scene['title'])

            item['date'] = ''
            if "last_modified" in scene or "date_created" in scene:
                if 'last_modified' in scene and scene['last_modified']:
                    item['date'] = self.parse_date(scene['last_modified']).strftime('%Y-%m-%d')
                elif 'date_created' in scene and scene['date_created']:
                    item['date'] = self.parse_date(scene['date_created']).strftime('%Y-%m-%d')

            if "allblackx" in meta['url']:
                item['site'] = "AllBlackX"
                item['parent'] = "XEmpire"
                item['url'] = f"https://www.allblackx.com/en/movie/{scene['url_title']}/{item['id']}"

            if "biphoria" in meta['url']:
                item['site'] = "BiPhoria"
                item['parent'] = "BiPhoria"
                item['url'] = f"https://www.biphoria.com/en/movie/{scene['url_title']}/{item['id']}"

            if "bskow" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = item['site']
                item['url'] = f"https://www.bskow.com/en/movie/{scene['url_title']}/{item['id']}"

            if "clubinfernodungeon" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = item['site']
                item['url'] = f"https://www.clubinfernodungeon.com/en/movie/{scene['url_title']}/{item['id']}"

            if "darkx" in meta['url']:
                item['site'] = "DarkX"
                item['parent'] = "XEmpire"
                item['url'] = f"https://www.darkx.com/en/movie/{scene['url_title']}/{item['id']}"

            if "devilsfilm" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = item['site']
                item['url'] = f"https://www.devilsfilm.com/en/dvd/{scene['url_title']}/{item['id']}"

            if "eroticax" in meta['url']:
                item['site'] = "EroticaX"
                item['parent'] = "XEmpire"
                item['url'] = f"https://www.eroticax.com/en/movie/{scene['url_title']}/{item['id']}"

            if "evilangel" in meta['url']:
                item['site'] = "Evil Angel"
                item['parent'] = "Evil Angel"
                item['url'] = f"https://www.evilangel.com/en/movie/{scene['url_title']}/{item['id']}"

            if "falconstudios" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = "Falcon Studios"
                item['url'] = f"https://www.falconstudios.com/en/movie/{scene['url_title']}/{item['id']}"

            if "fistingcentral" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = "Falcon Studios"
                item['url'] = f"https://www.falconstudios.com/en/movie/{scene['url_title']}/{item['id']}"

            if "genderxfilms" in meta['url']:
                item['site'] = "GenderXFilms"
                item['parent'] = "GenderXFilms"
                item['url'] = f"https://www.genderxfilms.com/en/movie/{scene['url_title']}/{item['id']}"

            if "girlfriendsfilms" in meta['url']:
                item['site'] = "GirlfriendsFilms"
                item['parent'] = "GirlfriendsFilms"
                item['url'] = f"https://www.girlfriendsfilms.com/en/movie/{scene['url_title']}/{item['id']}"

            if "hardx" in meta['url']:
                item['site'] = "HardX"
                item['parent'] = "XEmpire"
                item['url'] = f"https://www.hardx.com/en/movie/{scene['url_title']}/{item['id']}"

            if "lesbianx" in meta['url']:
                item['site'] = "LesbianX"
                item['parent'] = "XEmpire"
                item['url'] = f"https://www.lesbianx.com/en/movie/{scene['url_title']}/{item['id']}"

            if "lethalhardcore" in meta['url']:
                item['site'] = "Lethal Hardcore"
                item['parent'] = "Lethal Hardcore"
                item['url'] = f"https://www.lethalhardcore.com/en/movie/{scene['url_title']}/{item['id']}"

            if "peternorth" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = item['site']
                item['url'] = f"https://www.peternorth.com/en/dvd/{scene['url_title']}/{item['id']}"

            if "ragingstallion" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                item['parent'] = "Raging Stallion Studios"
                item['url'] = f"https://www.roccosiffredi.com/en/dvd/{scene['url_title']}/{item['id']}"

            if "roccosiffredi" in meta['url']:
                item['site'] = "Rocco Siffredi"
                item['parent'] = "Rocco Siffredi"
                item['url'] = f"https://www.roccosiffredi.com/en/dvd/{scene['url_title']}/{item['id']}"

            if "whiteghetto" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                if item['site'] == "3rd Degree":
                    item['site'] = "3rd Degree Films"
                if item['site'] == "White Ghetto Films":
                    item['site'] = "White Ghetto"
                item['parent'] = item['site']
                item['url'] = f"https://www.whiteghetto.com/en/dvd/{scene['url_title']}/{item['id']}"

            if "wicked" in meta['url']:
                item['site'] = scene['sitename_pretty']
                item['parent'] = scene['studio_name']
                item['url'] = f"https://www.wicked.com/en/movie/{scene['url_title']}/{item['id']}"

            if "zerotolerancefilms" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                if item['site'] == "3rd Degree":
                    item['site'] = "3rd Degree Films"
                item['parent'] = item['site']
                item['url'] = f"https://www.zerotolerancefilms.com/en/movie/{scene['url_title']}/{item['id']}"

            if "adulttime" in meta['url']:
                item['site'] = scene['_highlightResult']['studio_name']['value']
                if item['site'] == "3rd Degree":
                    item['site'] = "3rd Degree Films"
                item['parent'] = item['site']
                item['url'] = f"https://members.adulttime.com/en/dvd/{scene['url_title']}/{item['id']}"

            if not self.settings.get('local') and not self.settings.get('force_update'):
                submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], scene['_highlightResult']['sitename']['value'])
            else:
                submitmovie = True

            if "nb_of_scenes" in scene:
                scenecount = scene['nb_of_scenes']
            else:
                scenecount = 99

            if submitmovie and scenecount > 1 and item['date']:

                if 'description' in scene:
                    item['description'] = scene['description']
                elif 'description' in scene['_highlightResult']:
                    item['description'] = scene['_highlightResult']['description']['value']
                if 'description' not in item:
                    item['description'] = ''

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

                item['image'] = ''
                if scene['cover_path']:
                    item['image'] = f"https://images02-openlife.gammacdn.com/movies/{scene['cover_path']}_front_400x625.jpg"
                    item['image'] = item['image'].replace("movies//", "movies/")

                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                # ~ item['image_blob'] = ''

                item['type'] = 'Movie'
                # ~ print(item['title'], item['id'])
                if not ("zerotolerancefilms" in response.url and "wicked" in item['site'].lower()):
                    if "tbd" not in item['site'].lower():
                        yield self.check_item(item, self.days)

    def get_scenes(self, response):
        meta = response.meta
        movie = response.meta['movie']
        for scene in response.json()['results'][0]['hits']:
            item = SceneItem()
            item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]
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

            if scene['source_clip_id']:
                item['id'] = str(scene['source_clip_id'])
            else:
                item['id'] = str(scene['clip_id'])

            if 'title' in scene and scene['title']:
                item['title'] = scene['title']
            else:
                item['title'] = scene['movie_title']
                print(scene)
                print()
                print()
                print()
                print()
                print()
                print()

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
            shortsite = scene['sitename']
            if item['site'] == "3rd Degree":
                item['site'] = "3rd Degree Films"
            if item['site'] == "White Ghetto Films":
                item['site'] = "White Ghetto"
            if item['site'].lower() == "janedoe":
                item['site'] = "JaneDoePictures"
            if shortsite.lower() == "ragingstallion":
                item['site'] = "Raging Stallion Studios"

            item['parent'] = item['site']
            item['network'] = self.network

            if "allblackx" in meta['url']:
                item['url'] = f"https://www.allblackx.com/en/video/allblackx/{scene['url_title']}/{item['id']}"

            if "biphoria" in meta['url']:
                item['url'] = f"https://www.biphoria.com/en/video/biphoria/{scene['url_title']}/{item['id']}"

            if "bskow" in meta['url']:
                item['url'] = f"https://www.bskow.com/en/video/bskow/{scene['url_title']}/{item['id']}"

            if "clubinfernodungeon" in meta['url']:
                item['url'] = f"https://www.clubinfernodungeon.com/en/video/clubinfernodungeon/{scene['url_title']}/{item['id']}"

            if "darkx" in meta['url']:
                item['url'] = f"https://www.darkx.com/en/video/darkx/{scene['url_title']}/{item['id']}"

            if "devilsfilm" in meta['url']:
                item['url'] = f"https://www.devilsfilm.com/en/video/{shortsite}/{scene['url_title']}/{item['id']}"

            if "eroticax" in meta['url']:
                item['url'] = f"https://www.eroticax.com/en/video/eroticax/{scene['url_title']}/{item['id']}"

            if "evilangel" in meta['url']:
                item['url'] = f"https://www.evilangel.com/en/video/evilangel/{scene['url_title']}/{item['id']}"

            if "falconstudios" in meta['url']:
                item['url'] = f"https://www.falconstudios.com/en/video/falconstudios/{scene['url_title']}/{item['id']}"
                item['site'] = scene['studio_name']

            if "fistingcentral" in meta['url']:
                item['url'] = f"https://www.fistingcentral.com/en/video/fistingcentral/{scene['url_title']}/{item['id']}"
                item['site'] = scene['studio_name']

            if "genderxfilms" in meta['url']:
                item['url'] = f"https://www.genderxfilms.com/en/video/genderxfilms/{scene['url_title']}/{item['id']}"

            if "girlfriendsfilms" in meta['url']:
                item['url'] = f"https://www.girlfriendsfilms.com/en/video/girlfriendsfilms/{scene['url_title']}/{item['id']}"

            if "hardx" in meta['url']:
                item['url'] = f"https://www.hardx.com/en/video/hardx/{scene['url_title']}/{item['id']}"

            if "lesbianx" in meta['url']:
                item['url'] = f"https://www.lesbianx.com/en/video/lesbianx/{scene['url_title']}/{item['id']}"

            if "lethalhardcore" in meta['url']:
                item['url'] = f"https://www.lethalhardcore.com/en/video/lethalhardcore/{scene['url_title']}/{item['id']}"

            if "peternorth" in meta['url']:
                item['url'] = f"https://www.peternorth.com/en/video/peternorth/{scene['url_title']}/{item['id']}"

            if "ragingstallion" in meta['url']:
                item['url'] = f"https://www.ragingstallion.com/en/video/ragingstallion/{scene['url_title']}/{item['id']}"

            if "roccosiffredi" in meta['url']:
                item['url'] = f"https://www.roccosiffredi.com/en/video/roccosiffredi/{scene['url_title']}/{item['id']}"

            if "whiteghetto" in meta['url']:
                item['url'] = f"https://www.whiteghetto.com/en/video/whiteghetto/{scene['url_title']}/{item['id']}"

            if "wicked" in meta['url']:
                item['url'] = f"https://www.wicked.com/en/video/{scene['url_title']}/{item['id']}"

            if "zerotolerancefilms" in meta['url']:
                item['url'] = f"https://www.zerotolerancefilms.com/en/video/{scene['sitename']}/{scene['url_title']}/{item['id']}"

            movie['scenes'].append({'site': item['site'], 'external_id': item['id']})
            item['type'] = 'Scene'

            yield item

        # ~ print(movie['scenes'], movie['title'], movie['url'])
        yield movie

    def call_algolia_movie(self, page, token, referrer):
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }

        if 'allblackx' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aallblackx%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Aallblackx%22%5D%5D"}]}'

        if 'biphoria' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Abiphoria%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%5D&tagFilters="}]}'

        if 'bskow' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Abskow%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Abskow%22%5D%5D"}]}'

        if 'clubinfernodungeon' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aclubinfernodungeon%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%5D"}]}'

        if 'darkx' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adarkx%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Adarkx%22%5D%5D"}]}'

        if 'devilsfilm' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Adevilsfilm%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%5D&tagFilters=&facetFilters=%5B%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Asquirtalicious%22%2C%22availableOnSite%3Ahairyundies%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Adevilsfilmparodies%22%2C%22availableOnSite%3Agivemeteens%22%2C%22availableOnSite%3Aoutofthefamily%22%2C%22availableOnSite%3Adevilsgangbangs%22%2C%22availableOnSite%3AJaneDoePictures%22%2C%22availableOnSite%3Adevilstgirls%22%5D%5D"}]}'

        if 'eroticax' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aeroticax%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Aeroticax%22%5D%5D"}]}'

        if 'evilangel' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aevilangel%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%5D"}]}'

        if 'falconstudios' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afalconstudios%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Afalconstudios%22%2C%22availableOnSite%3Ahothouse%22%2C%22availableOnSite%3Afalconstudiospartners%22%5D%5D"}]}'

        if 'fistingcentral' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afistingcentral%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%5D"}]}'

        if 'genderxfilms' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Agenderxfilms%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20availableOnSite%3A\'genderxpartners\'%20AND%20NOT%20availableOnSite%3A\'evilangelpartners\'%20AND%20NOT%20availableOnSite%3A\'evilangelpartners\')%20AND%20(NOT%20categories.name%3A\'Compilation\')&facets=%5B%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%5D"}]}'

        if 'girlfriendsfilms' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Agirlfriendsfilms%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20categories.name%3A\'Compilation\'%20AND%20NOT%20categories.name%3A\'Member%20Compilation\')&facets=%5B%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%5D"}]}'

        if 'hardx' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ahardx%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Ahardx%22%5D%5D"}]}'

        if 'lesbianx' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ahardx%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Alesbianx%22%5D%5D"}]}'

        if 'lethalhardcore' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Alethalhardcore%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Alethalhardcore%22%2C%22availableOnSite%3Alethalhardcorevr%22%5D%5D"}]}'

        if 'peternorth' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apeternorth%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%5D&tagFilters=&facetFilters=%5B%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Apeternorth%22%5D%5D"}]}'

        if 'ragingstallion' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aragingstallion%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20studio_name%3A\'Naked%20Sword%20Originals\'%20AND%20NOT%20studio_name%3A\'Fetish%20Force\'%20AND%20NOT%20studio_name%3A\'Hot%20House\'%20AND%20NOT%20studio_name%3A\'Falcon%20Studios\')&facets=%5B%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%5D"}]}'

        if 'roccosiffredi' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aroccosiffredi%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%5D&tagFilters=&facetFilters=%5B%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Aroccosiffredi%22%2C%22availableOnSite%3Aroccosiffredipartners%22%5D%5D"},{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aroccosiffredi%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=nb_of_scenes&facetFilters=%5B%5B%22availableOnSite%3Aroccosiffredi%22%2C%22availableOnSite%3Aroccosiffredipartners%22%5D%5D"},{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aroccosiffredi%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22nb_of_scenes%3A-1%22%5D%5D"}]}'

        if 'whiteghetto' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Awhiteghetto%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%5D&tagFilters=&facetFilters=%5B%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Awhiteghetto%22%5D%5D"}]}'

        if 'wicked' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=30&maxValuesPerFacet=10&page=' + str(page) + '&filters=&facets=%5B%22availableOnSite%22%2C%22nb_of_scenes%22%2C%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%2C%5B%22nb_of_scenes%3A-1%22%5D%2C%5B%22availableOnSite%3Awicked%22%2C%22availableOnSite%3Awickedpartners%22%5D%5D"}]}'

        if 'zerotolerancefilms' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Azerotolerancefilms%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22is_movie_upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22is_movie_upcoming%3A-1%22%5D%5D"},{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Azerotolerancefilms%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=is_movie_upcoming"}]}'

        if 'adulttime' in referrer:
            jbody = '{"requests":[{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A"trans"%20OR%20content_tags%3A"straight"%20OR%20content_tags%3A"lesbian"%20OR%20content_tags%3A"gay"%20OR%20content_tags%3A"bisex")&facets=%5B%22categories.name%22%2C%22actors.name%22%2C%22nb_of_scenes%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22nb_of_scenes%3A-1%22%5D%5D"},{"indexName":"all_movies_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Advds%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22movie_id%22%2C%22title%22%2C%22cover_path%22%2C%22last_modified%22%2C%22actors%22%2C%22url_title%22%2C%22total_length%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22award_winning%22%2C%22nb_of_scenes%22%2C%22categories%22%2C%22full_movie%22%2C%22description%22%2C%22has_trailer%22%2C%22trailers%22%2C%22objectID%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(content_tags%3A"trans"%20OR%20content_tags%3A"straight"%20OR%20content_tags%3A"lesbian"%20OR%20content_tags%3A"gay"%20OR%20content_tags%3A"bisex")&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=nb_of_scenes"}]}'

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
