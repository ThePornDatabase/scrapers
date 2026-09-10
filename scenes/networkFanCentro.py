import datetime
import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkFanCentroSpider(BaseSceneScraper):
    name = 'FanCentro'
    network = 'FanCentro'

    # /lapi/feed is a 404 now and no replacement endpoint answers, so the feed can
    # no longer be paged.  The profile page server-renders its first page of results
    # into window.__REACT_QUERY_STATE__ under a "ModelFeed" query, which is where
    # the clips come from -- newest first, which is what an update run needs.
    start_urls = [
        ['Just Lucy', True, 'justlucy94'],
        ['Mdemma', True, 'mdemma'],
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        for link in self.start_urls:
            meta = {'page': self.page, 'site': link[0], 'parse_performer': link[1], 'siteid': link[2]}
            yield scrapy.Request(url=f"https://fancentro.com/{link[2]}", callback=self.parse,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        yield from self.get_scenes(response)

    def get_scenes(self, response):
        meta = self.copy_meta(response)

        state = re.search(r'window\.__REACT_QUERY_STATE__\s*=\s*(.*?);?\s*</script>', response.text, re.S)
        if not state:
            print(f"*** No embedded feed state on the {meta['siteid']} profile page")
            return
        try:
            queries = json.loads(state.group(1)).get('queries') or []
        except ValueError:
            return

        for query in queries:
            if 'ModelFeed' not in json.dumps(query.get('queryKey')):
                continue
            pages = ((query.get('state') or {}).get('data') or {}).get('pages') or []
            for entry in (i for p in pages for i in p.get('items', [])):
                # the feed mixes text posts in with the clips
                if entry.get('type') != 'video':
                    continue

                item = SceneItem()
                item['id'] = entry.get('id')
                item['title'] = self.cleanup_title(entry.get('title') or '')
                if not item['title']:
                    continue
                item['description'] = self.cleanup_description(entry.get('description') or '')

                published = entry.get('publishedAt')
                if published:
                    # epoch milliseconds
                    item['date'] = datetime.datetime.fromtimestamp(
                        int(published) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d')
                else:
                    item['date'] = None

                item['duration'] = self.duration_to_seconds(entry.get('duration') or '')

                image = ((entry.get('thumb') or {}).get('src') or '').strip()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image) if image else None

                item['performers'] = [meta['site']] if meta['parse_performer'] else []
                # the feed publishes tags as False when a clip carries none
                tags = entry.get('tags')
                item['tags'] = [t for t in tags if t] if isinstance(tags, list) else []

                item['trailer'] = ''
                item['type'] = 'Scene'
                item['site'] = f"FanCentro: {meta['site']}"
                item['parent'] = f"FanCentro: {meta['site']}"
                item['network'] = "FanCentro"

                link = entry.get('link') or f"/{meta['siteid']}/clips/{item['id']}/"
                item['url'] = f"https://fancentro.com{link}"

                item = self.check_item(item, self.days)
                if item:
                    yield item

    def duration_to_seconds(self, value):
        parsed = re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})$', (value or '').strip())
        if not parsed:
            return None
        hours, minutes, seconds = (int(x) if x else 0 for x in parsed.groups())
        return str(hours * 3600 + minutes * 60 + seconds)
