import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkOldNannSpider(BaseSceneScraper):
    name = 'OldNanny'
    network = 'Old Nanny Network'

    start_urls = [
        'https://oldnanny.com',
    ]

    # The tour was rebuilt on a "public-" BEM theme: the Bootstrap card/title-wrapp
    # markup is gone, and the scene page no longer carries a date at all -- it only
    # appears on the listing card, so get_scenes passes it through meta.
    selector_map = {
        'title': '//h1[@id="public-media-detail-title"]/text()',
        'description': '',
        'date': '',
        'date_formats': ['%b %d, %Y'],
        'image': '//video[contains(@class, "public-media-detail__video")]/@poster',
        'performers': '//a[contains(@class, "public-media-detail__model")]/text()',
        'tags': '//dd[contains(@class, "public-media-detail__tags")]/a/text()',
        'trailer': '//video[contains(@class, "public-media-detail__video")]/source/@src',
        'external_id': r'video/(.*?)/',
        'pagination': '/en/tour2/scenes/all?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        for scene in response.xpath('//article[contains(@class, "public-tour-card")]'):
            link = scene.xpath('.//a[contains(@href, "/video/")]/@href').get()
            if not link:
                continue
            link = self.format_link(response, link)
            if not re.search(self.get_selector_map('external_id'), link):
                continue

            # The card carries the only release date on the site, e.g. "Sep 04, 2026".
            # The old code passed date_formats=['%b %d, Y%'] -- a typo for '%Y'.
            scenedate = scene.xpath('.//span[contains(@class, "public-tour-card__date")]/text()').get()
            if scenedate:
                scenedate = self.parse_date(scenedate.strip(), date_formats=['%b %d, %Y'])
                if scenedate:
                    meta['date'] = scenedate.strftime('%Y-%m-%d')
            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = [s.replace(",", "") for s in performers]
        return performers

    def site_name(self, response):
        """The per-site brand now sits in the Information list as a <dt>Site</dt> pair."""
        return response.xpath('//dt[normalize-space(text())="Site"]/following-sibling::dd[1]/a/text()').get()

    def get_site(self, response):
        return self.site_name(response) or self.name

    def get_parent(self, response):
        return self.site_name(response) or self.name
