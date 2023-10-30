import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkChaosMenSpiderPerformers(BasePerformerScraper):
    name = 'ChaosMenAPIPerformers'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://www.chaosmen.com',
    ]

    image_sizes = [
        '500x750',
        '460x690',
        '240x360',
        '200x300',
        '150x225'
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
        page = int(self.page) - 1

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page + 1), callback=self.parse_token,
                                 meta={'page': page, 'url': link})

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia(response.meta['page'], token, response.meta['url'])

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
        # ~ referrerurl = response.meta["url"]
        for performer in response.json()['results'][0]['hits']:
            item = PerformerItem()

            item['name'] = string.capwords(performer['name'])
            item['network'] = 'Gamma Enterprises'
            item['url'] = f'https://www.{performer["sitename"]}.com/en/pornstar/view/{performer["url_name"]}/{performer["actor_id"]}'

            item['image'] = ''
            for size in self.image_sizes:
                if size in performer['pictures']:
                    item['image'] = f'https://images-fame.gammacdn.com/actors/{performer["actor_id"]}/{performer["actor_id"]}_{size}.jpg'
                    break
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image_blob'] = None

            item['bio'] = ''
            if 'description' in performer['_highlightResult']:
                if 'value' in performer['_highlightResult']['description']:
                    item['bio'] = performer['_highlightResult']['description']['value']

            item['gender'] = string.capwords(performer['gender'])
            if item['gender'] == 'Shemale':
                item['gender'] = 'Trans'
            item['birthday'] = ''
            item['astrology'] = ''
            item['birthplace'] = ''
            item['nationality'] = ''
            item['measurements'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['cupsize'] = ''
            item['fakeboobs'] = ''

            if 'attributes' in performer:
                if 'ethnicity' in performer['attributes']:
                    item['ethnicity'] = performer['attributes']['ethnicity']
                else:
                    item['ethnicity'] = ''

                if 'hair_color' in performer['attributes']:
                    item['haircolor'] = performer['attributes']['hair_color']
                else:
                    item['haircolor'] = ''

                if 'eye_color' in performer['attributes']:
                    item['eyecolor'] = performer['attributes']['eye_color']
                else:
                    item['eyecolor'] = ''

                if 'weight' in performer['attributes']:
                    item['weight'] = performer['attributes']['weight']
                else:
                    item['weight'] = ''

                if 'height' in performer['attributes']:
                    item['height'] = performer['attributes']['height']
                else:
                    item['height'] = ''

                if 'endowment' in performer['attributes']:
                    item['height'] = performer['attributes']['endowment']
                else:
                    item['fakeboobs'] = ''

            yield item

    def call_algolia(self, page, token, referrer):
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.27.1%3BJS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token
        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }
        # ~ jbody = '{"requests":[{"indexName":"all_actors_latest_desc","params":"query=&hitsPerPage=50&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3A%22%2C%22context%3Apornstars%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22actor_id%22%2C%22name%22%2C%22pictures%22%2C%22gender%22%2C%22sitename%22%2C%22url_name%22%2C%22last_release_date%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22description%22%2C%22attributes%22%2C%22objectID%22%2C%22shemale%22%2C%22male%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%5B%22content_tags%3Afemale%22%5D%2C%5B%22availableOnSite%3A%22%5D%5D"}]}'
        # ~ jbody = '{"requests":[{"indexName":"all_actors_latest_desc","params":"query=&hitsPerPage=84&maxValuesPerFacet=10&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atwentyonesextury%22%2C%22context%3Apornstars%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22actor_id%22%2C%22name%22%2C%22pictures%22%2C%22gender%22%2C%22sitename%22%2C%22url_name%22%2C%22last_release_date%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22description%22%2C%22attributes%22%2C%22objectID%22%2C%22shemale%22%2C%22male%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&facets=%5B%22availableOnSite%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3A%22%5D%5D"},{"indexName":"all_actors_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atwentyonesextury%22%2C%22context%3Apornstars%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22actor_id%22%2C%22name%22%2C%22pictures%22%2C%22gender%22%2C%22sitename%22%2C%22url_name%22%2C%22last_release_date%22%2C%22views%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22description%22%2C%22attributes%22%2C%22objectID%22%2C%22shemale%22%2C%22male%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite"}]}'
        jbody = '{"requests":[{"indexName":"all_actors_latest_desc","params":"query=&hitsPerPage=24&page=' + str(page) + '&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters="}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta={'token': token, 'page': page, 'url': referrer},
            callback=self.parse,
            headers=headers
        )
