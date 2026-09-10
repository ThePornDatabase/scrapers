import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWhornyFilmsSpider(BaseSceneScraper):
    name = 'WhornyFilms'
    network = 'Whorny Films'
    parent = 'Whorny Films'
    site = 'Whorny Films'

    start_urls = [
        'https://whornyfilms.com',
    ]

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 2,
    }

    # The WordPress/Elementor build is gone.  /blog/2021/08/04/search-and-filter/
    # 404s, and with it div.dce-item and every data-id selector the old spider hung
    # off.  The listing is /videos (page N at /videos?page=N) and each scene page
    # publishes a schema.org VideoObject holding the title, synopsis, still and
    # release date; the cast and runtime sit in the page's own header block.
    selector_map = {
        'title': '//h1[contains(@class, "vd-title")]/text()',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//div[contains(@class, "vd-meta-models")]/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'/videos/([^/?]+)',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "card-title-link")]/@href').getall()
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

    def get_title(self, response):
        title = (super().get_title(response)
                 or self.get_ld(response).get('name')
                 or response.xpath('//meta[@property="og:title"]/@content').get() or '')
        return self.cleanup_title(re.sub(r'\s*\|\s*WhornyFilms\s*$', '', title)) if title else ''

    def get_description(self, response):
        return self.cleanup_description(self.get_ld(response).get('description') or '')

    def get_date(self, response):
        published = self.get_ld(response).get('uploadDate') or self.get_ld(response).get('dateModified') or ''
        published = re.search(r'(\d{4}-\d{2}-\d{2})', published)
        return published.group(1) if published else None

    def get_image(self, response):
        image = (self.get_ld(response).get('thumbnailUrl')
                 or response.xpath('//meta[@property="og:image"]/@content').get() or '')
        image = image.strip()
        return self.format_link(response, image) if image else ''

    def get_duration(self, response):
        # the runtime is the second stat pill in the header, beside the view count
        for stat in response.xpath('//span[contains(@class, "vd-stat")]//text()').getall():
            runtime = re.search(r'(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\s*$', stat.strip())
            if runtime:
                hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
                return str(hours * 3600 + minutes * 60 + seconds)
        return None
