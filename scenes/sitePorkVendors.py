import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePorkVendorsSpider(BaseSceneScraper):
    name = 'PorkVendors'
    network = 'Pork Vendors'
    parent = 'Pork Vendors'
    site = 'Pork Vendors'

    start_urls = [
        'https://porkvendors.com',
    ]

    # Rebuilt on the Full Porn Network stack.  The listing URL is unchanged but
    # a.updateimg is gone -- cards are a.swimlane-scene-thumbnail-link now -- and on
    # the scene page h1.title_bar, p.description-text and the Date label block were
    # all replaced.  The page publishes a schema.org VideoObject carrying the title,
    # synopsis, still and release date, so those come from there.
    selector_map = {
        'title': '',
        'description': '',
        'date': '//label[contains(text(), "Date Added")]/parent::div//text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '',
        # scoped to the "Starring:" block -- the related-scene cards further down the
        # page link to /models/ too
        'performers': '//label[contains(text(), "Starring")]/parent::div//a[contains(@href, "/models/")]//text()',
        'tags': '//a[contains(@href, "/search.php?query=")]/text()',
        'trailer': '',
        'external_id': r'/trailers/([^/?]+)',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "swimlane-scene-thumbnail-link")]/@href').getall()
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
        title = (self.get_ld(response).get('name')
                 or response.xpath('//meta[@property="og:title"]/@content').get()
                 or response.xpath('//h1//text()').get() or '')
        return self.cleanup_title(title) if title.strip() else ''

    def get_description(self, response):
        return self.cleanup_description(self.get_ld(response).get('description') or '')

    def get_date(self, response):
        published = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_ld(response).get('uploadDate') or '')
        if published:
            return published.group(1)
        return super().get_date(response)

    def get_image(self, response):
        image = (self.get_ld(response).get('thumbnailUrl')
                 or response.xpath('//meta[@property="og:image"]/@content').get() or '')
        image = image.strip()
        return self.format_link(response, image) if image else ''

    def get_trailer(self, response):
        """contentUrl only ever points at a shared blurred placeholder clip, so it is
        deliberately not used as a trailer."""
        return ''
