import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLukesPOVSpider(BaseSceneScraper):
    name = 'LukesPOV'
    network = 'Lukes POV'
    parent = 'Lukes POV'
    site = 'Lukes POV'

    start_urls = [
        'https://lukespov.com/pov-blowjob-videos/',
    ]

    # The scene grid is a WordPress plugin: the first 12 cards are rendered into the
    # listing page, the rest come from admin-ajax.php.  /page/2/ exists but serves the
    # same first 12, so it cannot be used for pagination.
    ajax_url = 'https://lukespov.com/wp-admin/admin-ajax.php'

    selector_map = {
        'title': '//h1[@class="t"]/text()|//h1/text()',
        'description': '//div[@class="desc"]/p//text()',
        # Most scene pages carry no article:published_time; the JSON-LD VideoObject
        # is the reliable source, so get_date reads that first and falls back here.
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "perf")]//div[contains(@class, "nm")]/text()',
        # The site no longer tags scenes; the only link is the generic "videos" category
        'tags': '',
        'trailer': '',
        'external_id': r'lukespov\.com/(.*?)/',
        'type': 'Scene',
        'pagination': '',
    }

    async def start(self):
        # The base start_requests builds page one from 'pagination', which is unused
        # here because page one is just the listing URL.
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request(self.start_urls[0], callback=self.parse, meta=meta,
                             headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        """First page: cards are in the HTML, and the grid carries the ajax nonce."""
        grid = response.xpath('//div[@id="rw-grid"]')
        meta = self.copy_meta(response)
        meta['nonce'] = grid.xpath('./@data-nonce').get()
        meta['preset'] = grid.xpath('./@data-preset').get() or 'rw_scenes'
        meta['max'] = int(grid.xpath('./@data-max').get() or 1)

        yield from self.scene_requests(response, response)
        yield from self.next_ajax_page(meta)

    def parse_ajax(self, response, **kwargs):
        """Later pages arrive as {"data": {"html": "<cards>"}}."""
        payload = json.loads(response.text)
        html = (payload.get('data') or {}).get('html') or ''
        if not html.strip():
            return

        selector = scrapy.Selector(text=html)
        yield from self.scene_requests(selector, response)
        yield from self.next_ajax_page(response.meta)

    def next_ajax_page(self, meta):
        page = meta.get('page', 1) + 1
        if page > self.limit_pages or page > meta.get('max', 1) or not meta.get('nonce'):
            return
        newmeta = dict(meta)
        newmeta['page'] = page
        print('NEXT PAGE: ' + str(page))
        yield scrapy.FormRequest(
            url=self.ajax_url,
            formdata={'action': 'rw_load_more', 'nonce': meta['nonce'],
                      'preset': meta['preset'], 'paged': str(page)},
            headers={**self.headers, 'X-Requested-With': 'XMLHttpRequest'},
            callback=self.parse_ajax, meta=newmeta, dont_filter=True)

    def scene_requests(self, selector, response):
        for card in selector.xpath('//div[contains(@class, "rw-cardwrap")]'):
            link = card.xpath('.//a[contains(@class, "rw-card")]/@href').get()
            if not link:
                continue
            meta = {}
            title = card.xpath('.//*[contains(@class, "rw-card__title")]//text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)

            # Scene pages often carry no og:image and their JSON-LD thumbnailUrl is
            # just the site favicon, so the card's background image is the real source.
            style = card.xpath('.//div[contains(@class, "rw-card__bg")]/@style').get() or ''
            image = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
            if image and image.group(1).strip():
                meta['image'] = self.format_link(response, image.group(1).strip())
            yield scrapy.Request(url=self.format_link(response, link),
                                 callback=self.parse_scene, meta=meta)

    def get_video_object(self, response):
        """The JSON-LD VideoObject holds uploadDate and an ISO-8601 duration."""
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and entry.get('@type') == 'VideoObject':
                    return entry
        return {}

    def get_date(self, response):
        upload = self.get_video_object(response).get('uploadDate')
        if upload:
            upload = re.search(r'(\d{4}-\d{2}-\d{2})', upload)
            if upload:
                return upload.group(1)
        return super().get_date(response)

    def get_image(self, response):
        """Return '' rather than the bare domain when there is no usable image.

        The base implementation runs format_link() on an empty match, which resolves
        to the site root and yields an 'image' of https://lukespov.com.
        """
        image = self.get_video_object(response).get('thumbnailUrl') or ''
        # The JSON-LD falls back to the site favicon when a scene has no still
        if image and 'favicon' not in image.lower():
            return self.format_link(response, image)

        image = response.xpath(self.get_selector_map('image')).get() or ''
        image = image.strip()
        if not image:
            return ''
        return self.format_link(response, image)

    def get_duration(self, response):
        """The meta strip is a set of LABEL/VALUE pairs; only DURATION is wanted."""
        iso = self.get_video_object(response).get('duration')
        if iso:
            parts = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', iso.strip())
            if parts and any(parts.groups()):
                hours, minutes, seconds = (int(x or 0) for x in parts.groups())
                return str(hours * 3600 + minutes * 60 + seconds)
        for block in response.xpath('//div[@class="meta"]//div[@class="m"]'):
            label = block.xpath('.//div[@class="lbl"]/text()').get()
            if label and 'duration' in label.strip().lower():
                value = block.xpath('.//div[@class="val"]/text()').get()
                if value and re.search(r'\d+:\d{2}', value):
                    return self.duration_to_seconds(value.strip())
        return None
