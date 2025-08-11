import re
import string
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SitePlayboyPlusSpider(BaseSceneScraper):
    name = 'PlayboyPlus'
    network = 'PlayboyPlus'

    start_url = 'https://www.playboyplus.com'

    cookies = [{"name": "landingpage", "value": "%2F"}, {"name": "site_870", "value": "1"}, {"name": "origin", "value": "promo"}, {"name": "enterSite", "value": "true"}]

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        # ~ page = int(self.page) - 1
        page = int(self.page)
        start_url = f"https://www.playboyplus.com/en/updates/page/{str(page)}"
        yield scrapy.Request(start_url, callback=self.parse_token, meta={'page': page, 'url': self.start_url}, cookies=self.cookies, dont_filter=True)

    def parse_token(self, response):
        meta = response.meta
        token_script = response.xpath('//script[contains(text(), "algolia") and contains(text(), "apiKey")]/text()').get()
        meta['token'] = re.search(r"[\'\"]apiKey[\'\"].*?[\'\"](.*?)[\'\"]", token_script).group(1)
        return self.call_algolia(response.meta['page'], meta)

    def parse(self, response, **kwargs):
        meta = response.meta
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene
            if count:
                if 'page' in meta and meta['page'] < self.limit_pages:
                    meta['page'] = meta['page'] + 1
                    print(meta['page'])
                    yield scrapy.Request(url=self.get_next_page_url(self.start_url, meta['page']), callback=self.parse_token, meta={'page': meta['page'], 'url': self.start_url}, cookies=self.cookies, dont_filter=True)
                    # ~ yield self.call_algolia(meta['page'], meta)

    def get_scenes(self, response):
        cdn_host = "https://transform.gammacdn.com/media/"
        for scene in response.json()['results'][0]['hits']:
            if "clip_id" in scene and scene['clip_id']:
                item = self.init_scene()
                if scene['date_online']:
                    item['date'] = scene['date_online']
                    if item['date'] > "2025-07-07" and self.check_item(item, self.days):

                        largest_file = max(scene['multicontent_data']['nsfw'], key=lambda x: int(x['width']))['file']
                        item['image'] = cdn_host + largest_file
                        item['image_blob'] = self.get_image_blob_from_link(item['image'])

                        if len(scene['multicontent_data']['sfw']):
                            for sfw in scene['multicontent_data']['sfw']:
                                if sfw['name'] == "quarterCard":
                                    item['poster'] = cdn_host + sfw['file']
                                    item['poster_blob'] = self.get_image_blob_from_link(item['poster'])

                        item['id'] = scene['set_id']
                        item['title'] = string.capwords(scene['title'])
                        item['description'] = re.sub(r'<[^>]+>', '', scene['description'])
                        item['description'] = re.sub(r'[\r\n\t]+', ' ', item['description'])
                        item['description'] = re.sub(r'\s+', ' ', item['description'])

                        item['performers'], item['performers_data'] = self.get_performers_data(scene['actors'])

                        item['site'] = "PlayboyPlus"
                        item['parent'] = "PlayboyPlus"
                        item['network'] = "PlayboyPlus"
                        item['url'] = f"https://www.playboyplus.com/en/update/{scene['url_title']}/{scene['set_id']}"

                        if item['date'] > "2025-07-07":
                            yield self.check_item(item, self.days)

    def call_algolia(self, page, meta):
        token = meta['token']
        algolia_url = "https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser%3B%20instantsearch.js%20(4.64.3)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(7.5.5)%3B%20react-instantsearch-core%20(7.5.5)%3B%20JS%20Helper%20(3.16.2)"
        headers = {
            'referer': 'https://www.playboyplus.com/',
            'origin': 'https://www.playboyplus.com/',
            'x-algolia-api-key': token,
            'x-algolia-application-id': 'TSMKFA364Q',
            'Content-Type': 'application/json',
        }
        jbody = '{"requests":[{"indexName":"all_photosets_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Aplayboyplus%22%2C%22context%3Apictures%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22set_id%22%2C%22title%22%2C%22actors%22%2C%22picture%22%2C%22date_online%22%2C%22set_pictures%22%2C%22clip_id%22%2C%22clip_title%22%2C%22url_title%22%2C%22description%22%2C%22categories%22%2C%22views%22%2C%22num_of_pictures%22%2C%22objectID%22%2C%22directors%22%2C%22multicontent_data%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22availableOnSite%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22actors.name%22%2C%22categories.url_name%22%5D&filters=(upcoming%3A\'0\')%20AND%20availableOnSite%3Aplayboyplus%20OR%20availableOnSite%3Aplayboyplus-vip&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page - 1) + '&query=&tagFilters="}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta=meta,
            callback=self.parse,
            headers=headers
        )

    def get_performers_data(self, actors):
        perf_data = []
        performers = []

        for actor in actors:
            perf = {}
            perf['extra'] = {}
            performers.append(actor['name'])
            if "gender" in actor and actor['gender']:
                perf['name'] = string.capwords(actor['name'])
                perf['extra']['gender'] = string.capwords(actor['gender'])
                perf['network'] = "PlayboyPlus"
                perf['site'] = "PlayboyPlus"
                perf_data.append(perf)

        return performers, perf_data

    def get_image_from_link(self, image):
        if image and self.cookies:
            cookies = {cookie['name']: cookie['value'] for cookie in self.cookies}
            req = requests.get(image, cookies=cookies, verify=False)

            if req and req.ok:
                return req.content
        return None
