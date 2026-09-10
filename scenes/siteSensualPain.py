import base64
import json
import re

import requests
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSensualPainSpider(BaseSceneScraper):
    name = 'SensualPain'
    network = 'Sensual Pain'
    parent = 'Sensual Pain'
    site = 'Sensual Pain'

    start_urls = [
        'https://sensualpain.com',
    ]

    # The site was rebuilt as a "tracks" listing: /Videos.php is a 404, and with it
    # div.galleryEntry and the ID= scene links.  The catalogue is /tracks.php (a
    # single page of the newest releases, no pagination) and each scene lives at
    # /media.php?id=<slug>, where a schema.org MusicRecording carries the title,
    # synopsis, release date, runtime and the whole keyword set.
    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '',
        'external_id': r'[?&]id=([^&]+)',
        'trailer': '',
        'pagination': '/tracks.php',
    }

    def get_next_page_url(self, base, page):
        # one listing page; re-requesting it is dropped by the dupefilter, which is
        # what stops pagination
        return self.format_url(base, self.get_selector_map('pagination'))

    def get_scenes(self, response):
        cookies = response.headers.getlist("Set-Cookie")
        for card in response.xpath('//div[contains(@class, "track-card")]'):
            link = card.xpath('.//a[contains(@class, "track-title-link")]/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            meta['mycookies'] = cookies
            # the card carries the site's own zero-padded numeric id
            videoid = card.attrib.get('data-video-id')
            if videoid:
                meta['id'] = videoid

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_ld(self, response):
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and 'MusicRecording' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        title = (self.get_ld(response).get('name')
                 or response.xpath('//meta[@property="og:title"]/@content').get() or '')
        title = re.sub(r'\s*—\s*SensualPain\s*$', '', title)
        return self.cleanup_title(title) if title else ''

    def get_description(self, response):
        text = self.get_ld(response).get('description') or ''
        return self.cleanup_description(re.sub(r'\s+', ' ', text))

    def get_date(self, response):
        published = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_ld(response).get('datePublished') or '')
        return published.group(1) if published else None

    def get_duration(self, response):
        runtime = re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})', self.get_ld(response).get('duration') or '')
        if not runtime:
            return None
        hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
        return str(hours * 3600 + minutes * 60 + seconds)

    def get_tags(self, response):
        keywords = self.get_ld(response).get('keywords') or ''
        return [x.strip() for x in keywords.split(',') if x.strip()]

    def get_image_blob(self, response):
        image = super().get_image(response)
        if image:
            phpsessid = re.search(r'PHPSESSID=(.*?);', str(response.meta.get('mycookies', '')))
            if phpsessid:
                cookies_dict = {'PHPSESSID': phpsessid.group(1)}
            else:
                cookies_dict = ''

            header_dict = {'Referer': 'https://sensualpain.com'}
            return base64.b64encode(requests.get(image, headers=header_dict, cookies=cookies_dict).content).decode('utf-8')
        return None
