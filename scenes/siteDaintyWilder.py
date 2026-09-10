import json
import re

import scrapy
from cleantext import clean

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDaintyWilderSpider(BaseSceneScraper):
    name = 'DaintyWilder'
    site = 'DaintyWilder'
    parent = 'DaintyWilder'
    network = 'DaintyWilder'

    performer = 'Dainty Wilder'

    # The tour is a client-rendered Gatsby app served out of vsaspace, so
    # div.single-video never appears in the served HTML and the old selectors had
    # nothing to match. Gatsby still publishes the page's whole data set as
    # page-data.json, but under the CDN asset base rather than the site root, so
    # the base is read off the page's own script tags each run -- it carries a
    # build hash that changes whenever the site is rebuilt.
    start_urls = [
        'https://videos.daintywilder.com/',
    ]

    asset_base_re = r'(https://pub\.vsaspace\.com/[^/"\']+/assets/[^/"\']+/[^/"\']+)/'

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse_asset_base,
                                 meta={'page': self.page, 'home': link},
                                 headers=self.headers, cookies=self.cookies)

    def parse_asset_base(self, response):
        base = re.search(self.asset_base_re, response.text)
        if not base:
            print("*** Could not find the vsaspace asset base on %s" % response.url)
            return
        meta = self.copy_meta(response)
        yield scrapy.Request(url="%s/page-data/index/page-data.json" % base.group(1),
                             callback=self.parse_page_data, meta=meta, headers=self.headers)

    def get_video_nodes(self, response):
        try:
            data = json.loads(response.text)
        except ValueError:
            print("*** page-data.json did not parse for %s" % self.name)
            return []
        context = data.get('result', {}).get('pageContext', {})
        return context.get('videosData', {}).get('allAirtableVideos', {}).get('nodes') or []

    def parse_page_data(self, response):
        for node in self.get_video_nodes(response):
            data = node.get('data') or {}
            if data.get('Disabled'):
                continue

            title = data.get('Video_Title')
            if not title:
                continue

            item = self.init_scene()
            item['title'] = self.cleanup_title(clean(title, no_emoji=True))
            item['description'] = self.cleanup_description(clean(data.get('Video_Description') or '', no_emoji=True))
            item['id'] = data.get('UID') or data.get('DM_Video_Code') or ''

            # The store lists everything on one page; individual scenes have no
            # page of their own, which is why the old scraper also submitted the
            # site root as the URL.
            item['url'] = response.meta['home']

            # Nothing in the feed carries a release date, so it is left empty and
            # TPDB falls back to the import date.
            item['date'] = ''

            item['image'] = self.get_thumbnail(data)
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''

            item['performers'] = [self.performer]
            item['tags'] = [tag.strip().title() for tag in (data.get('Name__from_Tags_') or []) if tag and tag.strip()]

            duration = data.get('Duration')
            item['duration'] = str(int(duration)) if isinstance(duration, int) and duration > 1 else None

            item['trailer'] = self.get_preview(data)
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = 'Scene'

            if item['id']:
                yield self.check_item(item, self.days)

    @staticmethod
    def get_preview(data):
        # Video_Preview is a list of Airtable attachment objects, not a string.
        preview = data.get('Video_Preview')
        if isinstance(preview, list):
            for attachment in preview:
                if isinstance(attachment, dict) and attachment.get('url'):
                    return attachment['url']
            return ''
        return preview or ''

    @staticmethod
    def get_thumbnail(data):
        thumbnail = data.get('Thumbnail') or {}
        for local in thumbnail.get('localFiles') or []:
            images = (local.get('childImageSharp') or {}).get('gatsbyImageData', {}).get('images') or {}
            src = (images.get('fallback') or {}).get('src')
            if src:
                return src
        return ''
