import json
import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKingBBCSpider(BaseSceneScraper):
    name = 'KingBBC'
    network = 'King BBC'
    parent = 'King BBC'
    site = 'King BBC'

    start_urls = [
        'https://www.kingbbc.com',
    ]

    # The site was rebuilt and the siteData JSON blob the old spider parsed is gone.
    # /videos/page:N survives as a fallback route but serves the same page for every
    # N -- real pagination is /videos/page/N.  Each scene page publishes a
    # schema.org VideoObject with the title, synopsis, still, release date and
    # runtime; the cast is /model/ links and the only tags are the card's subtitle.
    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//a[contains(@href, "/model/")]//text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'/video/([^/?]+)',
        'pagination': '/videos/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//a[contains(@href, "/video/")][.//div[contains(@class, "thumb")]]'):
            link = card.attrib.get('href') or ''
            if not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            # tags are published only as the card subtitle, dot-separated
            subtitle = ' '.join(card.xpath('.//div[contains(@class, "sub")]//text()').getall())
            tags = [string.capwords(x.strip()) for x in re.split(r'[·|,]', subtitle) if x.strip()]
            if tags:
                meta['tags'] = tags

            preview = card.xpath('.//video/@data-src').get()
            if preview:
                meta['trailer'] = preview.strip()

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_ld(self, response):
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            entries = data.get('@graph') if isinstance(data, dict) and '@graph' in data else data
            for entry in (entries if isinstance(entries, list) else [entries]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        title = (self.get_ld(response).get('name')
                 or response.xpath('//h1//text()').get() or '')
        return self.cleanup_title(title) if title.strip() else ''

    def get_description(self, response):
        return self.cleanup_description(self.get_ld(response).get('description') or '')

    def get_date(self, response):
        published = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_ld(response).get('uploadDate') or '')
        return published.group(1) if published else None

    def get_image(self, response):
        image = self.get_ld(response).get('thumbnailUrl') or ''
        # thumbnailUrl is published as a list of duplicates
        if isinstance(image, list):
            image = image[0] if image else ''
        if not image:
            image = response.xpath('//meta[@property="og:image"]/@content').get() or ''
        image = image.strip()
        return self.format_link(response, image) if image else ''

    def get_duration(self, response):
        runtime = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', self.get_ld(response).get('duration') or '')
        if not runtime or not any(runtime.groups()):
            return None
        hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
        return str(hours * 3600 + minutes * 60 + seconds)

    def get_performers(self, response):
        return [x.strip() for x in
                response.xpath(self.get_selector_map('performers')).getall() if x.strip()]

    def get_tags(self, response):
        return response.meta.get('tags', [])

    def get_trailer(self, response):
        return response.meta.get('trailer', '')
