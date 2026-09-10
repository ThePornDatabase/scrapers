import re

from unidecode import unidecode

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLaFranceAPoilSpider(BaseSceneScraper):
    name = 'LaFranceAPoil'
    network = 'La France a Poil'
    parent = 'La France a Poil'
    site = 'La France a Poil'

    start_urls = [
        'https://www.lafranceapoil.com',
    ]

    cookies = {
        'disclaimerlfap': 'oui',
    }

    # The 403 was never a block on the site itself: it rejects requests that do
    # not look like a browser navigation. Sending the Accept / Sec-Fetch set below
    # returns 200 from the same exit that was getting 403 with a bare User-Agent.
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }

    # The tour was rebuilt: /portal/more.php is gone, the listing is /en/videos/N/
    # and scenes moved from /video?video=<id> to /en/video/<id>/<slug>/, so the
    # old external_id regex matched nothing and get_scenes yielded nothing.
    # Neither the cards nor the scene pages publish a release date any more, so
    # date is left empty for TPDB to fall back on the import date.
    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//a[contains(@href, "/model")]/text()',
        'tags': '//a[contains(@href, "categor")]/text()',
        'external_id': r'/video/(\d+)/',
        'trailer': '',
        'pagination': '/en/videos/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class, "thumb") and contains(@class, "item")]'
            '//a[contains(@href, "/video/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield response.follow(scene, callback=self.parse_scene)

    def clean_list(self, response, selector):
        # These link lists are introduced by a plain "Models" / "Categories"
        # label rendered as another anchor, which has to be dropped.
        values = []
        for value in response.xpath(self.get_selector_map(selector)).getall():
            value = self.cleanup_text(unidecode(value))
            if value and value.lower() not in ('models', 'model', 'categories', 'category', 'tags'):
                if value not in values:
                    values.append(value)
        return values

    def get_performers(self, response):
        return self.clean_list(response, 'performers')

    def get_tags(self, response):
        tags = self.clean_list(response, 'tags')
        if tags:
            tags.append("European")
        return tags

    def get_title(self, response):
        return self.cleanup_title(unidecode(super().get_title(response)))

    def get_description(self, response):
        return self.cleanup_description(unidecode(super().get_description(response)))
