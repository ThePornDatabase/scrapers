import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCosplaygroundSpider(BaseSceneScraper):
    name = 'Cosplayground'
    network = 'Cosplayground'
    parent = 'Cosplayground'
    site = 'Cosplayground'

    # The tour is a client-rendered Angular app on the NATS CMS ("natscms-app"),
    # so every path -- /sitemap.xml included -- returns the same shell and no
    # XPath can match anything. The catalogue comes from the CMS REST API instead:
    #
    #   1. <site>/natscms-app/config.json      -> natsUrl + cms_area_id
    #   2. <natsUrl>/tour_api.php/content/config -> pages and content servers
    #   3. .../content/page?slug=<page>        -> that page's layout blocks
    #   4. .../content/sets?cms_block_id=<id>  -> the sets themselves
    #
    # Every id is discovered at run time: cms_area_id and the block ids are
    # per-site and change whenever the tour is re-laid-out, so none is hardcoded.
    # Which fields a block returns depends on how it was configured, and only the
    # blocks wired to a single set carry the synopsis, so candidate blocks are
    # tried until one answers with descriptions.
    start_urls = [
        'https://cosplayground.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        for link in self.start_urls:
            yield scrapy.Request(url="%s/natscms-app/config.json" % link.rstrip('/'),
                                 callback=self.parse_app_config,
                                 meta={'page': self.page, 'home': link.rstrip('/')},
                                 headers=self.headers, cookies=self.cookies)

    def api_headers(self, area_id):
        headers = dict(self.headers or {})
        headers.update({
            'X-NATS-cms-area-id': area_id,
            'X-nats-entity-decode': '1',
            'Accept': 'application/json',
        })
        return headers

    def parse_app_config(self, response):
        try:
            config = json.loads(response.text)
        except ValueError:
            print("*** %s: natscms-app/config.json did not parse" % self.name)
            return

        meta = self.copy_meta(response)
        meta['nats_url'] = (config.get('natsUrl') or '').rstrip('/')
        meta['area_id'] = config.get('cms_area_id') or ''
        if not meta['nats_url'] or not meta['area_id']:
            print("*** %s: config.json carried no natsUrl/cms_area_id" % self.name)
            return

        yield scrapy.Request(
            url="%s/tour_api.php/content/config?cms_area_id=%s" % (meta['nats_url'], meta['area_id']),
            callback=self.parse_cms_config, meta=meta, headers=self.api_headers(meta['area_id']))

    def parse_cms_config(self, response):
        try:
            config = json.loads(response.text)
        except ValueError:
            print("*** %s: content/config did not parse" % self.name)
            return

        meta = self.copy_meta(response)
        meta['content_server'] = self.get_content_server(config)

        # The list page and the detail page each carry set-backed blocks; both are
        # walked because only some of them return the synopsis.
        # Tours differ on whether the detail route is /videos/:slug or /video/:slug,
        # so both the list and detail routes are taken from the config rather than
        # assumed, and the detail route also supplies the prefix for scene URLs.
        slugs, detail = [], ''
        for page in config.get('pages') or []:
            slug = (page or {}).get('slug') if isinstance(page, dict) else None
            if not slug or not re.match(r'^/videos?(/:[a-z_]+)?$', slug):
                continue
            slugs.append(slug)
            if '/:' in slug:
                detail = slug.split('/:')[0]
        if not slugs:
            print("*** %s: no videos page in the CMS config" % self.name)
            return

        meta['detail_path'] = detail or '/videos'
        meta['page_slugs'] = slugs
        meta['block_ids'] = []
        yield self.request_page(meta)

    def request_page(self, meta):
        slug = meta['page_slugs'].pop(0)
        return scrapy.Request(
            url="%s/tour_api.php/content/page?slug=%s" % (meta['nats_url'], slug),
            callback=self.parse_blocks, meta=meta, headers=self.api_headers(meta['area_id']),
            dont_filter=True)

    def parse_blocks(self, response):
        meta = self.copy_meta(response)
        try:
            page = json.loads(response.text)
        except ValueError:
            page = {}

        for block in page.get('blocks') or []:
            source = (block.get('settings') or {}).get('ds_source')
            block_id = block.get('cms_block_id')
            if block_id and source and source != 'notset' and block_id not in meta['block_ids']:
                meta['block_ids'].append(block_id)

        if meta['page_slugs']:
            yield self.request_page(meta)
        elif meta['block_ids']:
            yield self.request_sets(meta)
        else:
            print("*** %s: no set-backed blocks found" % self.name)

    def request_sets(self, meta):
        block_id = meta['block_ids'].pop(0)
        return scrapy.Request(
            url="%s/tour_api.php/content/sets?cms_block_id=%s" % (meta['nats_url'], block_id),
            callback=self.parse_sets, meta=meta, headers=self.api_headers(meta['area_id']),
            dont_filter=True)

    def parse_sets(self, response):
        meta = self.copy_meta(response)
        try:
            sets = json.loads(response.text).get('sets') or []
        except ValueError:
            sets = []

        # Keep looking for a block whose sets carry a synopsis; fall back to the
        # last block that returned anything at all.
        has_description = any((entry.get('description') or '').strip() for entry in sets)
        if sets and not has_description and meta['block_ids']:
            yield self.request_sets(meta)
            return
        if not sets:
            if meta['block_ids']:
                yield self.request_sets(meta)
            return

        for entry in sets:
            item = self.build_item(entry, meta)
            if item:
                yield self.check_item(item, self.days)

    def build_item(self, entry, meta):
        if str(entry.get('deleted') or '0') != '0':
            return None
        title = (entry.get('name') or '').strip()
        set_id = entry.get('cms_set_id')
        if not title or not set_id:
            return None

        item = self.init_scene()
        item['title'] = self.cleanup_title(title)
        item['id'] = str(set_id)
        item['url'] = "%s%s/%s" % (meta['home'], meta.get('detail_path') or '/videos',
                                   entry.get('slug') or '')

        description = entry.get('description') or ''
        item['description'] = self.cleanup_description(re.sub(r'<[^>]+>', ' ', description))
        item['performers'] = self.get_cast(description)

        scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', entry.get('added_nice') or '')
        item['date'] = scenedate.group(1) if scenedate else ''

        item['image'] = self.get_image_url(entry, meta.get('content_server'))
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''

        item['tags'] = []
        item['trailer'] = ''
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['type'] = 'Scene'
        return item

    @staticmethod
    def get_cast(description):
        # The synopses bold each performer's name, and nothing else, so that is
        # the only cast list the API exposes.
        names = []
        for name in re.findall(r'<strong>\s*([^<]{2,40}?)\s*</strong>', description or ''):
            name = re.sub(r'\s+', ' ', name).strip(' .,:;')
            if name and name not in names:
                names.append(name)
        return names

    @staticmethod
    def get_content_server(config):
        for server in (config.get('servers') or {}).values():
            url = ((server or {}).get('settings') or {}).get('url')
            if url:
                return url.rstrip('/')
        return ''

    @staticmethod
    def get_image_url(entry, content_server):
        thumbs = ((entry.get('preview_formatted') or {}).get('thumb')) or {}
        if not thumbs or not content_server:
            return ''
        # Sizes are keyed "<width>-<height>"; the largest is a full-resolution
        # original, so the next one down is used as the poster.
        try:
            sizes = sorted(thumbs, key=lambda k: int(k.split('-')[0]))
        except ValueError:
            sizes = list(thumbs)
        for key in reversed(sizes[:-1] or sizes):
            entries = thumbs.get(key) or []
            if entries and entries[0].get('fileuri'):
                signature = entries[0].get('signature') or ''
                return "%s%s%s" % (content_server, entries[0]['fileuri'],
                                   ('?' + signature) if signature else '')
        return ''
