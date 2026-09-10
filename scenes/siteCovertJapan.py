import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCovertJapanSpider(BaseSceneScraper):
    name = 'CovertJapan'
    network = 'Sex Like Real'
    parent = 'Sex Like Real'
    site = 'CovertJapan'
    max_pages = 15

    start_urls = [
        'https://www.covertjapan.com',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': True,
                       'AUTOTHROTTLE_DEBUG': False,
                       'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
                       'CONCURRENT_REQUESTS': 1,
                       'DOWNLOAD_DELAY': 2
                       }

    # The site was rebuilt on Joomla as a VOD store: h2[@itemprop="name"],
    # div#details and div#images are gone, and the meta keywords tag list with them.
    # The listing keeps its ?start= paging (16 per page) but the cards are
    # div.blog-item, and the scene page carries the title, a Joomla tag list and the
    # player -- but no synopsis and no release date, so the blurb and the still come
    # off the card.  As before, no date is published anywhere on the site.
    selector_map = {
        'title': '//div[contains(@class, "com-content-article")]//h1/text()',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//a[contains(@href, "/models/") and string-length(@href) > 9]/text()',
        'tags': '//ul[contains(@class, "tags")]//a[not(contains(@href, "/studios/"))]/text()',
        'external_id': r'/videos/([^/?]+)',
        'trailer': '',
        'pagination': '/en/videos?start=%s'
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % ((int(page) - 1) * 16))

    def get_scenes(self, response):
        for card in response.xpath('//div[contains(@class, "blog-item")]'):
            link = card.xpath('.//figure//a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            image = card.xpath('.//figure//img/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)
            blurb = card.xpath('.//p/span[contains(@class, "field-value")]/text()').get()
            if blurb:
                meta['description'] = self.cleanup_description(re.sub(r'\s+', ' ', blurb))

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        return response.meta.get('image', '')

    def get_description(self, response):
        return response.meta.get('description', '')

    def get_tags(self, response):
        """The Joomla tag list mixes real tags with the studio and the performer
        name, so the studio links are excluded by the selector and the cast is
        dropped here."""
        performers = {x.lower() for x in self.get_performers(response)}
        tags = []
        for tag in response.xpath(self.get_selector_map('tags')).getall():
            tag = tag.strip()
            if tag and tag.lower() not in performers and tag not in tags:
                tags.append(tag)
        return tags
