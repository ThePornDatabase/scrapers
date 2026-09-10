import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteSweetyXSpider(BaseSceneScraper):
    name = 'SweetyX'
    network = 'SweetyX'
    parent = 'SweetyX'
    site = 'SweetyX'

    # sweetyx.com now redirects onto the SexPacker tour, and every card there
    # links to the join page rather than to a scene page -- there are no scene
    # pages left to fetch, so the item is built entirely from the card.  That
    # leaves no synopsis, cast or release date anywhere on the site; dates are
    # left empty for TPDB to fall back on the import date.  The tour serves its
    # whole catalogue on one page, so there is no pagination to walk.
    url = 'https://www.sweetyx.com/en/sweetyx-videos'

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        yield scrapy.Request(url=self.url, callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        for card in response.xpath('//div[@class="videos__video"]'):
            thumb = card.xpath('.//div[contains(@class, "videos__thumbnail")]')
            sceneid = thumb.xpath('./@data-click-id').get()
            title = card.xpath('.//a[contains(@class, "videos__videoTitle")]/text()').get()
            if not sceneid or not title:
                continue

            item = self.init_scene()
            item['title'] = self.cleanup_title(title)
            item['id'] = sceneid.strip()
            item['url'] = response.url
            item['date'] = ''
            item['description'] = ''
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''

            image = thumb.xpath('.//img/@src').get()
            item['image'] = image.strip() if image else ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''

            item['duration'] = self.get_card_duration(thumb)
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)

    def get_card_duration(self, thumb):
        # The badge reads like "HD 27:14".
        info = thumb.xpath('.//span[contains(@class, "videos__videoInfo")]/text()').get()
        if info:
            match = re.search(r'((?:\d{1,2}:)?\d{1,2}:\d{2})', info)
            if match:
                return self.duration_to_seconds(match.group(1))
        return None
