import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        "blackmeatwhitefeet.com": "Black Meat White Feet",
        "blacksonblondes.com": "Blacks on Blondes",
        "blacksoncougars.com": "Blacks on Cougars",
        "cuckoldsessions.com": "Cuckold Sessions",
        "cumbang.com": "Cumbang",
        "gloryhole-initiations.com": "Gloryhole Initiations",
        "gloryhole.com": "Gloryhole",
        "interracialblowbang.com": "Interracial Blowbang",
        "interracialpickups.com": "Interracial Pickups",
        "watchingmydaughtergoblack.com": "Watching My Daughter Go Black",
        "watchingmymomgoblack.com": "Watching My Mom Go Black",
        "wefuckblackgirls.com": "We Fuck Black Girls",
        "zebragirls.com": "Zebra Girls"
    }
    return match.get(argument, argument)


# The Algolia index identifies a site by a bare slug, where the old page markup
# gave a hostname.  These map the slug back onto the site names the scraper has
# always submitted; anything not listed falls back to the index's own
# sitename_pretty rather than inventing a name.
SITE_SLUGS = {
    "blackmeatwhitefeet": "blackmeatwhitefeet.com",
    "blacksonblondes": "blacksonblondes.com",
    "blacksoncougars": "blacksoncougars.com",
    "cuckoldsessions": "cuckoldsessions.com",
    "cumbang": "cumbang.com",
    "gloryhole-initiations": "gloryhole-initiations.com",
    "gloryhole": "gloryhole.com",
    "interracialblowbang": "interracialblowbang.com",
    "interracialpickups": "interracialpickups.com",
    "watchingmydaughtergoblack": "watchingmydaughtergoblack.com",
    "watchingmymomgoblack": "watchingmymomgoblack.com",
    "wefuckblackgirls": "wefuckblackgirls.com",
    "zebragirls": "zebragirls.com",
}


class networkDogfartSpider(BaseSceneScraper):
    name = 'Dogfart'
    network = "Dogfart Network"
    parent = "Dogfart Network"

    # The tour was rebuilt on Gamma's React stack: /tour/scenes/ is a 404 and the
    # home page ships no scene markup at all, so div.recent-updates and every field
    # selector had nothing to match.  The catalogue is an Algolia index instead.
    # Its API key is issued per page load and carries a validUntil, so it is scraped
    # from the home page on each run rather than hard-coded, and the key is refused
    # without a matching Referer.
    start_urls = [
        'https://www.dogfartnetwork.com/',
    ]

    algolia_app_id = 'TSMKFA364Q'
    algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries'
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
            print("*** Could not find the Algolia API key on the Dogfart home page")
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
            # the key is issued against this referer and 403s without it
            'Referer': 'https://www.dogfartnetwork.com/',
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

    def get_scenes(self, response):
        try:
            results = json.loads(response.text)['results'][0]
        except (ValueError, KeyError, IndexError):
            return

        for hit in results.get('hits') or []:
            item = SceneItem()

            item['title'] = self.cleanup_title(hit.get('title') or '')
            if not item['title']:
                continue

            item['description'] = self.cleanup_description(hit.get('description') or '')
            item['id'] = str(hit.get('clip_id') or hit.get('objectID') or '')

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', hit.get('release_date') or '')
            item['date'] = scenedate.group(1) if scenedate else None

            slug = hit.get('sitename') or ''
            item['url'] = "https://www.dogfartnetwork.com/en/video/%s/%s/%s" % (
                slug, hit.get('url_title') or '', item['id'])

            item['site'] = (match_site(SITE_SLUGS[slug]) if slug in SITE_SLUGS
                            else (hit.get('sitename_pretty') or '').strip() or "Dogfart Network")
            item['parent'] = self.parent
            item['network'] = self.network

            item['performers'] = [a['name'].strip() for a in (hit.get('actors') or [])
                                  if isinstance(a, dict) and (a.get('name') or '').strip()]
            item['tags'] = [c['name'].strip().title() for c in (hit.get('categories') or [])
                            if isinstance(c, dict) and (c.get('name') or '').strip()]

            pictures = hit.get('pictures') or {}
            image = pictures.get('1920x1080') or pictures.get('resized') or ''
            item['image'] = ("https://images01-fame.gammacdn.com/movies" + image) if image else ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

            trailers = hit.get('trailers') or {}
            item['trailer'] = next((trailers[q] for q in ('1080p', '720p', '480p', '360p', '240p', '160p')
                                    if trailers.get(q)), '')

            length = hit.get('length')
            item['duration'] = str(int(length)) if length else None
            item['type'] = 'Scene'

            item = self.check_item(item, self.days)
            if item:
                yield item
