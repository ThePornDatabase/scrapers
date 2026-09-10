import json
import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteWaterAndPowerSpider(BaseSceneScraper):
    name = 'WaterAndPower'
    network = 'Water And Power'
    parent = 'Water And Power'
    site = 'Water And Power'

    start_urls = [
        'https://water-and-power.com',
    ]

    # The site is no longer a Gatsby build: every /page-data/**/page-data.json is a
    # 404.  It now renders server-side, listing scenes at /scenes (page N at
    # /scenes/N) and giving each scene a /scene/<slug> page.  A scene is a set of
    # parts, and the page publishes them as a schema.org ItemList of VideoObjects
    # carrying the title, synopsis, still, runtime, release date and preview for
    # each part -- one TPDB scene per part, as before.
    selector_map = {
        'external_id': r'/videos/([^/?]+)',
        'pagination': '/scenes/%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return self.format_url(base, '/scenes')
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "card")][contains(@href, "/scene/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                 headers=self.headers, cookies=self.cookies)

    def get_parts(self, response):
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            if not isinstance(data, dict) or 'ItemList' not in str(data.get('@type')):
                continue
            for entry in data.get('itemListElement') or []:
                part = entry.get('item') if isinstance(entry, dict) else None
                if isinstance(part, dict) and 'VideoObject' in str(part.get('@type')):
                    yield part

    def parse_scene(self, response):
        # The cast is only published on the part cards, keyed by the same URL the
        # VideoObject carries.
        cast = {}
        for card in response.xpath('//a[contains(@class, "card")][contains(@href, "/videos/")]'):
            names = card.xpath('.//div[@class="card__girls"]/text()').get() or ''
            cast[card.attrib.get('href', '').rstrip('/')] = [
                string.capwords(x.strip()) for x in names.split(',') if x.strip()]

        for part in self.get_parts(response):
            url = (part.get('url') or '').strip()
            if not url or not re.search(self.get_selector_map('external_id'), url):
                continue

            item = SceneItem()
            item['title'] = self.cleanup_title(part.get('name') or '')
            item['description'] = self.cleanup_description(
                re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', part.get('description') or '')))
            item['url'] = url
            item['id'] = re.search(self.get_selector_map('external_id'), url).group(1)

            upload = re.search(r'(\d{4}-\d{2}-\d{2})', part.get('uploadDate') or '')
            item['date'] = upload.group(1) if upload else None

            image = (part.get('thumbnailUrl') or '').strip()
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(image) if image else None

            item['trailer'] = (part.get('contentUrl') or '').strip()
            item['duration'] = self.duration_to_seconds(part.get('duration') or '')

            performers = cast.get(re.sub(r'^https?://[^/]+', '', url).rstrip('/'), [])
            # a part occasionally repeats the same model twice
            item['performers'] = list(dict.fromkeys(performers))
            item['tags'] = []
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = 'Scene'

            item = self.check_item(item, self.days)
            if item:
                yield item

    def duration_to_seconds(self, value):
        """The ld+json publishes ISO-8601 durations (PT15M25S)."""
        parsed = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', value or '')
        if not parsed or not any(parsed.groups()):
            return None
        hours, minutes, seconds = (int(x) if x else 0 for x in parsed.groups())
        return str(hours * 3600 + minutes * 60 + seconds)
