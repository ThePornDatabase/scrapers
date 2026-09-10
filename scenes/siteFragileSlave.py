import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFragileSlaveSpider(BaseSceneScraper):
    name = 'FragileSlave'
    network = 'Fragile Slave'
    parent = 'Fragile Slave'
    site = 'Fragile Slave'

    # Every page redirects to /warning-page until the splash is accepted.  Hitting
    # /enter sets the session cookie, after which the tour is readable; Scrapy's
    # cookie middleware carries it through the rest of the crawl.
    start_urls = [
        'https://fragileslave.com/enter',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="videocontent"]/p/text()',
        # The site no longer publishes a release date, on the listing or the scene page
        'date': '',
        'performers': '//span[@class="update_models"]/a/text() | //a[contains(@href, "/models/")]/text()',
        'tags': '//a[contains(@href, "/tags/")]/text()',
        'external_id': r'/updates/(.*?)/?$',
        'trailer': '',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        return self.format_url('https://fragileslave.com', self.get_selector_map('pagination') % page)

    def start_requests(self):
        # Overridden so the first request is the splash-page accept, not a listing
        yield scrapy.Request(self.start_urls[0], callback=self.after_enter,
                             headers=self.headers, cookies=self.cookies)

    def after_enter(self, response):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request(self.get_next_page_url('https://fragileslave.com', self.page),
                             callback=self.parse, meta=meta, headers=self.headers)

    def get_scenes(self, response):
        # The listing carries the thumbnail and the numeric content id, so both are
        # passed through rather than re-derived from the scene page.
        for scene in response.xpath('//div[contains(@class, "modelfeature")]'):
            link = scene.xpath('.//div[@class="modelimg"]/a/@href').get()
            if not link or '/updates/' not in link:
                continue

            meta = {}
            image = scene.xpath('.//img[contains(@class, "update_thumb")]/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)

            scene_id = scene.xpath('.//img[contains(@class, "update_thumb")]/@id').get()
            if scene_id:
                meta['id'] = scene_id

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        # The p.date block reads "34 Photos, 06:48 Video | Tags:" - only the clip
        # length is wanted, and the photo count would otherwise be parsed as time.
        info = response.xpath('//p[@class="date"]/text()').get()
        if info:
            duration = re.search(r'(\d{1,3}:\d{2}(?::\d{2})?)', info)
            if duration:
                return self.duration_to_seconds(duration.group(1))
        return None
