import re
import string
import scrapy
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        '18tokyo': 'Japanese Teens',
        'analnippon': 'Anal Nippon',
        'bigtitstokyo': 'Big Tits Tokyo',
        'bukkakenow': 'Bukkake Now',
        'japaneseflashers': 'Japanese Flashers',
        'japanesematures': 'Japanese Matures',
        'japaneseslurp': 'Japanese Slurp',
        'jcosplay': 'Japanese Cosplay',
        'jpmilfs': 'JP Milfs',
        'jpnurse': 'JP Nurse',
        'jpshavers': 'Shaved Pussy',
        'jpteacher': 'Japanese Teacher',
        'jschoolgirls': 'Japanese School Girls',
        'myracequeens': 'My Race Queens',
        'ocreampies': 'O Creampies',
        'officesexjp': 'Japanese Office Sex',
        'outdoorjp': 'Outdoor JP',
        'povjp': 'POVJP',
        'tokyobang': 'Tokyo Bang',
        'wierdjapan': 'Weird Japan',
    }
    return match.get(argument, '')


class NetworkAllJapanesePassSpider(BaseSceneScraper):
    name = 'AllJapanesePass'
    network = "All Japanese Pass"
    parent = "All Japanese Pass"

    start_urls = [
        'https://18tokyo.com',
        'https://analnippon.com',
        'https://bigtitstokyo.com',
        'https://bukkakenow.com',
        'https://japaneseflashers.com',
        'https://japanesematures.com',
        'https://japaneseslurp.com',
        'https://jcosplay.com',
        'https://jpmilfs.com',
        'https://jpnurse.com',
        'https://jpshavers.com',
        'https://jpteacher.com',
        'https://jschoolgirls.com',
        'https://myracequeens.com',
        'https://ocreampies.com',
        'https://officesexjp.com',
        'https://outdoorjp.com',
        'https://povjp.com',
        'https://tokyobang.com',
        #'https://wierdjapan.com',  #Requires Membership
    ]

    # The tour was rebuilt on a tube-style theme: the b-breadcrumb / itemprop markup
    # is gone and div.block-details renders empty (its contents are filled in by
    # script), so the scene page only reliably yields og:title and og:image.  The
    # listing card carries the runtime and preview, which get_scenes passes through.
    selector_map = {
        'title': '//meta[@property="og:title"]/@content|//h1/text()',
        'description': '',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': True,
        'performers': '',
        'tags': '',
        'external_id': r'/video/(\d+)/',
        'trailer': '',
        'pagination': '/latest-updates/%s'
    }

    def get_scenes(self, response):
        # the b-videos-item-link class is gone; each card is a div.item whose anchor
        # points straight at /video/<id>/<slug>
        for card in response.xpath('//div[contains(@class, "item")][.//a[contains(@href, "/video/")]]'):
            scene = card.xpath('.//a[contains(@href, "/video/")]/@href').get()
            if not scene or not re.search(self.get_selector_map('external_id'), scene):
                continue
            meta = {}
            runtime = card.xpath('.//div[@class="duration"]/text()').get()
            if runtime and ':' in runtime:
                meta['duration'] = self.duration_to_seconds(runtime.strip())
            trailer = card.xpath('.//img/@data-preview').get()
            if trailer:
                meta['trailer'] = trailer.strip()
            image = card.xpath('.//img/@data-original').get()
            if image and image.strip():
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = response.xpath(self.get_selector_map('title')).get()
        if title:
            title = string.capwords(title)
            return title.strip()

        return None

    def get_site(self, response):
        parsed_uri = tldextract.extract(response.url)
        domain = parsed_uri.domain
        site = match_site(domain)
        if not site:
            site = tldextract.extract(response.url).domain

        return site

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                return list(map(lambda x: x.strip().title(), tags.getall()))

        return []

    def get_performers(self, response):
        # guard the empty selector the way get_tags above does: process_xpath falls
        # through to css() for anything not starting with // and then raises on ''
        if not self.get_selector_map('performers'):
            return []
        performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        if performers:
            if "Japanese AV Model" in performers:
                performers.remove("Japanese AV Model")
            if "Unknown Model" in performers:
                performers.remove("Unknown Model")
            if "Amateur" in performers:
                performers.remove("Amateur")
            return list(map(lambda x: x.strip(), performers))

        return []

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')
            if image:
                image = image.replace(" ", "%20")
                return self.format_link(response, image)

        return None
