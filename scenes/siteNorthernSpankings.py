import html
import json
import re
from urllib.parse import urlencode

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# The site is a Next.js front end over a mymember.site backend. The listing API
# (/api/cancellable-request) only exposes id/title/date/duration/poster — no
# description, tags or performers — and fetchVideosApi is the only whitelisted
# function name, so scene detail has to come from the scene page itself. That
# page ships its data as a React Server Component payload split across
# self.__next_f.push() calls, which is what the helpers below reassemble.
_RSC_CHUNK_RE = re.compile(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', re.S)
_RSC_TEXT_REF_RE = re.compile(r'(?:^|\n)([0-9a-f]+):T([0-9a-f]+),')
_HTML_TAG_RE = re.compile(r'<[^>]+>')


class SiteNorthernSpankingsSpider(BaseSceneScraper):
    name = 'NorthernSpankings'
    network = 'Northern Spanking'
    parent = 'Northern Spanking'
    site = 'Northern Spanking'

    start_url = 'https://northernspanking.com'
    api_url = 'https://northernspanking.com/api/cancellable-request'

    # Modest throttling — this is a small site (80 scenes total) and every scene
    # costs a full page render.
    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 30,
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1,
        'RETRY_HTTP_CODES': [429, 408, 500, 502, 503, 504, 522, 524],
        'RETRY_PRIORITY_ADJUST': -1,
    }

    headers = {
        'Accept': 'application/json',
        'Referer': 'https://northernspanking.com/',
    }

    # Everything is pulled out of the RSC payload by hand, so the selector map
    # only carries what BaseSceneScraper needs structurally.
    selector_map = {
        'external_id': r'/(\d+)-',
        'pagination': '',
        'type': 'Scene',
    }

    per_page = 30

    def api_page_url(self, page):
        args = [[
            f'page={page}',
            'sortBy=date_added:desc',
            f'count={self.per_page}',
            f'newCount={self.per_page}',
            'query[]=status=published,scheduled',
        ], False]
        query = urlencode({'functionName': 'fetchVideosApi',
                           'args': json.dumps(args, separators=(',', ':'))})
        return f'{self.api_url}?{query}'

    async def start(self):
        yield scrapy.Request(self.api_page_url(self.page),
                             callback=self.parse_listing,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies,
                             dont_filter=True)

    def parse_listing(self, response):
        data = json.loads(response.text).get('data') or {}
        videos = data.get('data') or []
        page = int(data.get('current_page') or response.meta.get('page') or 1)
        last_page = int(data.get('last_page') or 1)
        self.logger.info(f"Listing page {page}/{last_page} — {len(videos)} videos (total {data.get('total')})")

        for video in videos:
            video_id = video.get('id')
            if not video_id:
                continue
            # /videos/<id> redirects to the canonical /<content_mapping_id>-<slug> URL.
            yield scrapy.Request(f'{self.start_url}/videos/{video_id}',
                                 callback=self.parse_scene,
                                 meta={'video_id': video_id},
                                 headers={'Referer': self.headers['Referer']},
                                 dont_filter=True)

        if page < last_page and page < self.limit_pages:
            yield scrapy.Request(self.api_page_url(page + 1),
                                 callback=self.parse_listing,
                                 meta={'page': page + 1},
                                 headers=self.headers,
                                 dont_filter=True)

    def parse_scene(self, response):
        video_id = response.meta.get('video_id')
        payload = self.rsc_payload(response.text)
        if not payload:
            self.logger.warning(f'No RSC payload found for {response.url}')
            return

        video = self.extract_video(payload, video_id)
        if not video:
            self.logger.warning(f'Could not locate video {video_id} in payload for {response.url}')
            return

        item = self.init_scene()
        item['id'] = video.get('id') or video_id
        item['title'] = self.cleanup_text(video.get('title') or '')
        item['description'] = self.strip_html(self.resolve_ref(video.get('description'), payload))
        item['date'] = (video.get('publish_date') or video.get('original_publish_date') or '')[:10]
        item['url'] = response.url

        item['performers'] = [c['screen_name'] for c in (video.get('casts') or []) if c.get('screen_name')]
        item['tags'] = [t['name'] for t in (video.get('tags') or []) if t.get('name')]

        duration = video.get('duration')
        item['duration'] = str(int(duration)) if duration else ''

        # poster_src is a signed CloudFront URL that eventually expires, so pull
        # the blob down now rather than relying on the link staying good.
        item['image'] = video.get('poster_src') or ''
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['type'] = 'Scene'

        yield self.check_item(item, self.days)

    # ------------------------------------------------------------------ #
    # RSC payload helpers                                                  #
    # ------------------------------------------------------------------ #

    def rsc_payload(self, body):
        """Reassemble the Next.js flight payload from its script chunks."""
        parts = []
        for chunk in _RSC_CHUNK_RE.findall(body):
            try:
                parts.append(json.loads('"' + chunk + '"'))
            except ValueError:
                continue
        return ''.join(parts)

    def extract_video(self, payload, video_id):
        """Pull the video object out of the payload.

        Anchors on `"data":{"id":<video_id>,` and lets the JSON decoder find the
        object's end, so nested braces inside strings (the signed CDN URLs are
        full of them) can't throw off the match.
        """
        anchor = re.search(r'"data":\{"id":%s\s*,' % re.escape(str(video_id)), payload)
        if not anchor:
            return None
        start = payload.index('{', anchor.start() + len('"data":') - 1)
        try:
            obj, _ = json.JSONDecoder().raw_decode(payload[start:])
        except ValueError as e:
            self.logger.warning(f'Failed to decode video object for {video_id}: {e}')
            return None
        return obj if isinstance(obj, dict) else None

    def resolve_ref(self, value, payload):
        """Resolve an RSC string reference ("$4b") to its text chunk.

        Long strings are hoisted out of the object into `<id>:T<hexlen>,<text>`
        chunks, with the length given in UTF-8 bytes.
        """
        if not isinstance(value, str):
            return ''
        if not value.startswith('$'):
            return value
        ref = value[1:]
        for match in _RSC_TEXT_REF_RE.finditer(payload):
            if match.group(1) != ref:
                continue
            length = int(match.group(2), 16)
            return payload[match.end():].encode('utf-8')[:length].decode('utf-8', 'ignore')
        return ''

    def strip_html(self, text):
        if not text:
            return ''
        text = re.sub(r'</p>|<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = _HTML_TAG_RE.sub('', text)
        text = html.unescape(text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()
