import re
import json
import html
import string
import urllib.parse
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class FakingsSpider(BaseSceneScraper):
    name = 'Fakings'
    network = 'FA Kings'

    url = 'https://www.fakings.com'

    # Every /en/serie/<name>/N path in the old list now 404s -- the site dropped its
    # per-series listings, which is where the 43 404s in a crawl came from.  The main
    # search listing survives, but without the .htm extension or the ?all parameter.
    paginations = [
        '/en/buscar/%s',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//a[contains(@href, "/actrices-porno/")]/text()',
        'tags': '',
        'external_id': r'/en/video/(.+?)/?$',
        'trailer': '',
        'pagination': '/en/buscar/%s'
    }

    async def start(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = self.copy_meta(response)
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        # div.zona-listado2 is gone; the listing is a Tailwind rebuild whose cards
        # link straight to /en/video/<slug>, repeated per card, hence the dedupe.
        scenes = response.xpath('//a[contains(@href, "/en/video/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene),
                                     callback=self.parse_scene,
                                     headers=self.headers, cookies=self.cookies)

    def get_ld(self, response):
        """The scene page publishes a schema.org VideoObject holding the title,
        synopsis, still, release date and trailer -- none of which the rebuilt
        markup exposes as addressable elements any more."""
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        title = self.get_ld(response).get('name') or ''
        if not title:
            title = response.xpath('//meta[@property="og:title"]/@content').get() or ''
            title = re.sub(r'^FAKINGS\s*\|\s*', '', title)
        return self.cleanup_title(title) if title else ''

    def get_description(self, response):
        text = self.get_ld(response).get('description') or ''
        if not text:
            return ''
        text = re.sub(r'<[^>]+>', ' ', html.unescape(text))
        return self.cleanup_description(re.sub(r'\s+', ' ', text))

    def get_date(self, response):
        upload = self.get_ld(response).get('uploadDate') or ''
        upload = re.search(r'(\d{4}-\d{2}-\d{2})', upload)
        return upload.group(1) if upload else None

    def get_image(self, response):
        image = (self.get_ld(response).get('thumbnailUrl')
                 or response.xpath('//meta[@property="og:image"]/@content').get() or '')
        image = image.strip()
        return self.format_link(response, image) if image else ''

    def get_trailer(self, response):
        return (self.get_ld(response).get('contentUrl') or '').strip()

    def get_performers(self, response):
        """Only the cast links carry names; the nav link to the index is excluded."""
        names = []
        for a in response.xpath('//a[contains(@href, "/actrices-porno/")]'):
            href = a.attrib.get('href') or ''
            if href.rstrip('/').endswith('actrices-porno'):
                continue
            name = ' '.join(a.xpath('.//text()').getall()).strip()
            if name and name not in names:
                names.append(string.capwords(name))
        return names

    def get_site(self, response):
        site = response.xpath('//strong[contains(., "Serie")]//following-sibling::a/text()')
        return site.get().strip() if site else "FaKings"

