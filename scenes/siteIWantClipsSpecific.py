import re
import datetime
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIWantClipsSpecificSpider(BaseSceneScraper):
    name = 'IWantClipsSpecific'
    network = 'I Want Clips'

    start_urls = [
        'https://iwantclips.com',
    ]

    cookies = {'accepted': '1', 'member_id': '0'}

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')
        page = int(self.page) - 1

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page + 1), callback=self.parse_token, meta={'page': page, 'url': link}, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        return f"https://iwantclips.com/store/537048/K8-Morgan?page={page}"

    def parse_token(self, response):
        match = re.search(r'searchClient.*?, \'(.*?)\'', response.text)
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
        # ~ print(response.json())
        for scene in response.json()['results'][0]['hits']:
            item = SceneItem()

            item['image'] = scene['thumbnail_url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if 'preview_mp4_url' in scene:
                item['trailer'] = scene['preview_mp4_url']
                if "https" not in item['trailer'].lower():
                    item['trailer'] = None
            else:
                item['trailer'] = None
            item['id'] = scene['content_id']
            item['title'] = string.capwords(scene['title'])
            item['description'] = scene['description']

            if scene['publish_date']:
                item['date'] = datetime.datetime.utcfromtimestamp(scene['publish_date']).isoformat()
                # ~ print(f"Datetime: {scene['publish_date']}     Parsed_date: {item['date']}")
            else:
                print("Date not provided, using today")
                item['date'] = self.parse_date('today').isoformat()

            item['performers'] = [scene['model_username']]
            item['tags'] = scene['categories'] + scene['keywords']
            item['tags'] = [i for i in item['tags'] if i]

            item['site'] = "I Want Clips"
            item['parent'] = "I Want Clips"
            item['network'] = "I Want Clips"
            item['url'] = scene['content_url']

            yield self.check_item(item, self.days)

    def call_algolia(self, page, token, referrer):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        # ~ algolia_url = 'https://n95emuhkii-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(3.4.0)%3B%20JS%20Helper%202.26.1&x-algolia-application-id=N95EMUHKII&x-algolia-api-key=' + token
        algolia_url = 'https://n95emuhkii-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(3.4.0)%3B%20JS%20Helper%202.26.1&x-algolia-application-id=N95EMUHKII&x-algolia-api-key=' + token

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }
        # ~ jbody = '{"requests":[{"indexName":"prod_main_page","params":"query=&page=' + str(page) + '&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&clickAnalytics=true&facets=%5B%5D&tagFilters="}]}'
        jbody = '{"requests":[{"indexName":"v1_artist_page","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&clickAnalytics=true&facets=%5B%22categories%22%2C%22categories%22%2C%22categories%22%2C%22categories%22%5D&tagFilters="}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta={'token': token, 'page': page, 'url': referrer},
            callback=self.parse,
            headers=headers
        )
