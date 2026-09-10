import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePlayboyTVSpider(BaseSceneScraper):
    name = 'PlayboyTV'
    site = 'Playboy TV'
    parent = 'Playboy TV'
    network = 'Playboy'

    # The tour moved to Gamma's React stack, so /episodes ships no li.item markup
    # at all -- the catalogue is an Algolia index scoped to the playboytv segment.
    # The API key is issued per page load and carries a validUntil, so it is
    # scraped from the tour on every run, and it is refused without a matching
    # Referer.
    start_urls = [
        'https://www.playboytv.com/',
    ]

    algolia_app_id = 'TSMKFA364Q'
    algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries'
    image_base = 'https://images01-fame.gammacdn.com/movies'
    hits_per_page = 60

    selector_map = {
        'external_id': r'/(\d+)/?$',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_api_key,
                             meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def parse_api_key(self, response):
        apikey = re.search(r'"apiKey"\s*:\s*"([^"]+)"', response.text)
        if not apikey:
            print("*** Could not find the Algolia API key on the %s tour" % self.name)
            return
        meta = self.copy_meta(response)
        meta['apikey'] = apikey.group(1)
        yield self.algolia_request(meta)

    def algolia_request(self, meta):
        body = json.dumps({"requests": [{
            "indexName": "all_scenes_latest_desc",
            "params": "query=&hitsPerPage=%d&page=%d&filters=upcoming%%3A0" % (
                self.hits_per_page, int(meta['page']) - 1),
        }]})
        headers = {
            'x-algolia-application-id': self.algolia_app_id,
            'x-algolia-api-key': meta['apikey'],
            'Content-Type': 'application/json',
            'Referer': self.start_urls[0],
        }
        return scrapy.Request(url=self.algolia_url, method='POST', body=body,
                              headers=headers, callback=self.parse, meta=meta,
                              dont_filter=True)

    def parse(self, response, **kwargs):
        count = 0
        for scene in self.get_scenes(response):
            count += 1
            yield scene

        if count and response.meta['page'] < self.limit_pages:
            meta = self.copy_meta(response)
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield self.algolia_request(meta)

    def get_scene_url(self, hit, sceneid):
        return "https://www.playboytv.com/en/episode/%s/%s/%s" % (
            hit.get('sitename') or 'playboytv', hit.get('url_title') or '', sceneid)

    def get_scene_title(self, hit):
        # The tour has always submitted these as "Show - Episode"; the index keeps
        # the show in serie_name and the episode in title.
        title = self.cleanup_title(hit.get('title') or '')
        show = self.cleanup_title(hit.get('serie_name') or '')
        if show and title:
            return "%s - %s" % (show, title)
        return title or show

    def get_scenes(self, response):
        try:
            results = json.loads(response.text)['results'][0]
        except (ValueError, KeyError, IndexError):
            return

        for hit in results.get('hits') or []:
            item = SceneItem()

            item['title'] = self.get_scene_title(hit)
            if not item['title']:
                continue

            item['id'] = str(hit.get('clip_id') or hit.get('objectID') or '')
            item['description'] = self.cleanup_description(hit.get('description') or '')
            item['url'] = self.get_scene_url(hit, item['id'])

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', hit.get('release_date') or '')
            item['date'] = scenedate.group(1) if scenedate else None

            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network

            item['performers'] = [a['name'].strip() for a in (hit.get('actors') or [])
                                  if isinstance(a, dict) and (a.get('name') or '').strip()]
            item['tags'] = [c['name'].strip().title() for c in (hit.get('categories') or [])
                            if isinstance(c, dict) and (c.get('name') or '').strip()]

            pictures = hit.get('pictures') or {}
            image = next((pictures[q] for q in ('1920x1080', '960x544', '638x360', 'resized')
                          if isinstance(pictures.get(q), str)), '')
            item['image'] = (self.image_base + image) if image else ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

            trailers = hit.get('trailers') or {}
            item['trailer'] = next((trailers[q] for q in ('1080p', '720p', '540p', '480p', '360p', '240p', '160p')
                                    if trailers.get(q)), '')

            length = hit.get('length')
            item['duration'] = str(int(length)) if length else None
            item['type'] = 'Scene'

            item = self.check_item(item, self.days)
            if item:
                yield item
