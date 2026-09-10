import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VRLifeSpider(BaseSceneScraper):
    name = 'VRLife'
    network = 'VRLife'
    parent = 'VRLife'
    start_urls = [
        'https://virtualrealporn.com',
        'https://virtualrealtrans.com',
        'https://virtualrealpassion.com',
        'https://virtualrealgay.com',
        'https://virtualrealjapan.com',
        'https://virtualrealamateurporn.com',
    ]

    cookies = {
        'av-accepted': '1'
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    }

    # The sites were rebuilt on Livewire: div.videoItem with its data-id and
    # a.w-portfolio-item-anchor is gone, and so is the Movie-typed JSON-LD the old
    # parse_scene looked for.  Cards are div.card[wire:key] now, and each scene page
    # publishes a schema.org VideoObject holding the title, synopsis, still,
    # release date, runtime, cast and genres -- so everything comes from there.
    selector_map = {
        'external_id': r'/([^/]+)/?$',
        'pagination': '/?videoPage=%s'
    }

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "card")][.//a[contains(@class, "card-link")]]'):
            url = card.xpath('.//a[contains(@class, "card-link")]/@href').get()
            if not url:
                continue
            meta = {}
            # the numeric id only exists on the card
            sceneid = re.search(r'video-card-(\d+)', card.attrib.get('wire:key') or '')
            if sceneid:
                meta['id'] = sceneid.group(1)
            yield scrapy.Request(url=self.format_link(response, url), callback=self.parse_scene,
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

    def parse_scene(self, response):
        data = self.get_ld(response)
        if not data:
            return

        item = SceneItem()
        item['title'] = self.clean_title(self.cleanup_title(data.get('name') or ''))
        if not item['title']:
            return
        item['description'] = self.cleanup_description(data.get('description') or '')

        image = (data.get('thumbnailUrl') or '').strip()
        item['image'] = image
        item['image_blob'] = self.get_image_blob_from_link(image) if image else None

        sceneid = response.meta.get('id')
        if not sceneid:
            sceneid = re.search(r'/videos/(\d+)/', image or '')
            sceneid = sceneid.group(1) if sceneid else None
        item['id'] = sceneid

        item['trailer'] = (data.get('contentUrl') or '').strip()
        item['duration'] = self.duration_to_seconds(data.get('duration') or '')
        item['url'] = response.url

        published = re.search(r'(\d{4}-\d{2}-\d{2})', data.get('uploadDate') or '')
        item['date'] = published.group(1) if published else None

        item['network'] = self.network
        item['parent'] = self.parent
        item['site'] = self.get_site(response)
        item['type'] = 'Scene'

        actors = data.get('actor') or []
        if isinstance(actors, dict):
            actors = [actors]
        item['performers'] = [a['name'].strip() for a in actors
                              if isinstance(a, dict) and (a.get('name') or '').strip()]

        tags = [x.strip() for x in (data.get('genre') or []) if x and x.strip()]
        if "VR" not in tags:
            tags.append("VR")
        item['tags'] = tags

        item = self.check_item(item, self.days)
        if item:
            yield item

    def duration_to_seconds(self, value):
        """The VideoObject publishes ISO-8601 durations, usually as bare seconds
        (PT2487S) but occasionally with hour and minute parts."""
        parsed = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', value or '')
        if not parsed or not any(parsed.groups()):
            return None
        hours, minutes, seconds = (int(x) if x else 0 for x in parsed.groups())
        return str(hours * 3600 + minutes * 60 + seconds)

    @staticmethod
    def clean_title(title):
        # virtualrealjapan.com uses funky brackets, cleaning up for astethics
        return title.replace("【", "[").replace("】", "] ")
