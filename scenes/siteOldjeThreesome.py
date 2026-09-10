import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteOldje3someSpider(BaseSceneScraper):
    name = 'Oldje3some'
    network = 'Oldje'
    parent = 'Oldje'
    site = 'Oldje 3some'

    start_urls = [
        'https://www.oldje-3some.com',
    ]

    # The tour was rebuilt on an "ssl-" theme.  /page/N and /videos both 302 to
    # error404.php, and /gallery/N renders its cards client-side, so neither the old
    # pagination nor div.read-more exists any more.  Every page does carry a
    # window.sslSearchItems array holding the whole catalogue -- title, cast,
    # runtime, still and URL for all of it -- so the listing comes from there in a
    # single request and each scene page is visited only for its release date.
    selector_map = {
        'title': '//div[contains(@class, "ssl-detail-content")]/h1/text()',
        'description': '',
        'date': '//div[contains(@class, "ssl-detail-meta")]//span[contains(., ", 20")]//text()',
        're_date': r'(\w{3} \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '',
        'performers': '',
        'tags': '//div[contains(@class, "ssl-detail-categories")]//a/text()',
        'trailer': '',
        'external_id': r'/videos/([0-9a-f]+)',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request(self.start_urls[0], callback=self.parse, meta=meta,
                             headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        yield from self.get_scenes(response)

    def get_scenes(self, response):
        catalogue = re.search(r'window\.sslSearchItems\s*=\s*(\[.*?\]);', response.text, re.S)
        if not catalogue:
            return
        try:
            entries = json.loads(catalogue.group(1))
        except ValueError:
            return

        for entry in entries:
            link = (entry.get('url') or '').strip()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = {}
            if entry.get('title'):
                meta['title'] = self.cleanup_title(entry['title'])
            # "actors" is a single comma-separated string
            performers = [x.strip() for x in (entry.get('actors') or '').split(',') if x.strip()]
            if performers:
                meta['performers'] = performers
            runtime = entry.get('duration') or ''
            if ':' in runtime:
                meta['duration'] = self.duration_to_seconds(runtime.strip())
            thumb = (entry.get('thumb') or '').strip()
            if thumb:
                meta['image'] = self.format_link(response, thumb)
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            yield scrapy.Request(url=self.format_link(response, link),
                                 callback=self.parse_scene, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_title(self, response):
        title = super().get_title(response)
        if not title:
            title = response.meta.get('title')
        return title.strip() if title else None
