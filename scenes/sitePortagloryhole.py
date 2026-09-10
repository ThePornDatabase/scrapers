import re
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePortagloryholeSpider(BaseSceneScraper):
    name = 'PortaGloryhole'
    network = 'PortaGloryhole'
    parent = 'PortaGloryhole'
    site = 'PortaGloryhole'

    start_urls = [
        'https://www.portagloryhole.com',
    ]

    cookies = [{"name":"americancumdolls_locale","value":"en"},{"name":"device_view","value":"full"},{"name":"americancumdolls_adult_warning","value":"1"}]

    selector_map = {
        'description': '//h2[contains(@class, "description")]/text()',
        'performers': '//a[@class="tags" and contains(@href, "/models/")]/text()',
        'tags': '//a[@class="tags" and contains(@href, "search")]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        # /videos?page=N now serves an empty 12KB shell with no cards; the root is
        # the only page that still lists anything
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        """Build items from the listing cards.

        Every card's links now point at /join -- the per-scene pages are gone, so
        the crawl used to request /join a few times and finish with nothing.  The
        card still carries the post id, title, still, release date and runtime,
        which is everything reachable without a membership.  parse_scene below is
        left in place but is no longer reached; note it also carried a
        `date < 2018-12-31` backfill guard that would have dropped every current
        scene anyway.
        """
        for card in response.xpath('//div[contains(@class, "post_item")]'):
            item = self.init_scene()

            item['id'] = card.attrib.get('data-post-id')
            title = card.xpath('.//div[contains(@class, "post_video")]/a[1]/@title').get()
            if not item['id'] or not title or not title.strip():
                continue
            item['title'] = self.cleanup_title(title)
            item['url'] = response.url
            item['description'] = ''

            scenedate = card.xpath('.//span[contains(@class, "posted_on")]/text()').get()
            if scenedate:
                scenedate = self.parse_date(scenedate.strip(), date_formats=['%b %d, %Y'])
                if scenedate:
                    item['date'] = scenedate.strftime('%Y-%m-%d')

            duration = card.xpath('.//i[contains(@class, "fa-video")]/following-sibling::text()').get()
            if duration and ':' in duration:
                item['duration'] = self.duration_to_seconds(duration.strip())

            image = (card.xpath('.//img[contains(@class, "item_cover")]/@src').get()
                     or card.xpath('.//a[@data-media-poster]/@data-media-poster').get())
            if image:
                item['image'] = image.strip()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['site'] = self.get_site(response)
            item['parent'] = self.get_parent(response)
            item['network'] = self.network

            yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image and self.cookies:
            cookies = {cookie['name']:cookie['value'] for cookie in self.cookies}
            req = requests.get(image, cookies=cookies, verify=False)

            if req and req.ok:
                return req.content
        return None
