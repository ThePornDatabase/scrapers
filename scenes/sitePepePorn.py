import html
import json
import re
import string

import scrapy
from deep_translator import GoogleTranslator

from tpdb.BaseSceneScraper import BaseSceneScraper


class FakingsSpider(BaseSceneScraper):
    name = 'PepePorn'
    network = 'FA Kings'
    parent = 'PepePorn'
    site = 'PepePorn'

    url = 'https://www.pepeporn.com'

    # The site was rebuilt on Next.js: /videos/N.htm is a 404 and div.zona-listado2
    # is gone, along with every scene-page selector that hung off it.  The listing
    # is a single /videos page (no paging), and each scene page publishes a
    # schema.org VideoObject carrying the title, synopsis, still, release date and
    # the video itself.  As with the sibling Fakings scraper, the cast is the
    # /actrices-porno/ links.
    start_urls = [
        'https://www.pepeporn.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//a[contains(@href, "/actrices-porno/")]',
        'tags': '',
        'external_id': r'/video/([^/?]+)',
        'trailer': '',
        'pagination': '/videos',
    }

    async def start(self):
        yield scrapy.Request(url=self.format_url(self.url, self.get_selector_map('pagination')),
                             callback=self.parse, meta={'page': self.page},
                             headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        yield from self.get_scenes(response)

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href, "/video/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     headers=self.headers, cookies=self.cookies)

    def get_ld(self, response):
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    @staticmethod
    def translate(text):
        """A translation failure should cost the field, not the whole item."""
        try:
            return GoogleTranslator(source='es', target='en').translate(text) or ''
        except Exception:
            return ''

    def get_title(self, response):
        title = (self.get_ld(response).get('name') or '').strip()
        if not title:
            return ''
        translated = self.translate(title.lower())
        return string.capwords(translated) if translated else self.cleanup_title(title)

    def get_description(self, response):
        text = self.get_ld(response).get('description') or ''
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(text))).strip()
        if not text:
            return ''
        return (self.translate(text) or text).strip()

    def get_date(self, response):
        published = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_ld(response).get('uploadDate') or '')
        return published.group(1) if published else None

    def get_image(self, response):
        image = (self.get_ld(response).get('thumbnailUrl')
                 or response.xpath('//meta[@property="og:image"]/@content').get() or '')
        image = image.strip()
        return self.format_link(response, image) if image else ''

    def get_trailer(self, response):
        return (self.get_ld(response).get('contentUrl') or '').strip()

    def get_performers(self, response):
        """The nav link to the index has to be excluded, and a name can appear twice
        on the page."""
        performers = []
        for a in response.xpath(self.get_selector_map('performers')):
            href = a.attrib.get('href') or ''
            if href.rstrip('/').endswith('actrices-porno'):
                continue
            name = ' '.join(a.xpath('.//text()').getall()).strip()
            if name and name not in performers:
                performers.append(string.capwords(name))
        return performers

    def get_tags(self, response):
        return ['Latina', 'Latin American']
