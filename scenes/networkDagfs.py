import re
from urllib.parse import urlparse
import tldextract
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'brokenbabes': "Broken Babes",
        'brokenteens': "Broken Teens",
        'brutalclips': "Brutal Clips",
        'bustygfsexposed': "Busty GFs Exposed",
        'dagfs': "dagfs",
        'fhuta': "Fuck Her Up The Ass",
        'frenchgfs': "French GFs",
        'realasianexposed': "Real Asian Exposed",
        'realblackexposed': 'Real Black Exposed',
        'realemoexposed': 'Real Emo Exposed',
        'realgfsexposed': 'Real GFs Exposed',
        'reallatinaexposed': 'Real Latina Exposed',
        'reallesbianexposed': "Real Lesbians Exposed",
        'realmomexposed': "Real Mom Exposed",
    }
    return match.get(argument, argument)


class NetworkDaGFsSpider(BaseSceneScraper):
    name = 'Dagfs'
    network = 'dagfs'

    start_urls = [
        'https://brokenbabes.com',
        'https://brokenteens.com',
        'https://brutalclips.com',
        'https://bustygfsexposed.com',
        'https://dagfs.com',
        'https://fhuta.com',
        'https://frenchgfs.com',
        'https://realasianexposed.com',
        'https://realblackexposed.com',
        'https://realemoexposed.com',
        'https://realgfsexposed.com',
        'https://reallatinaexposed.com',
        'https://reallesbianexposed.com',
        'https://realmomexposed.com',
    ]

    selector_map = {
        'title': '//section[@class="scene"]//h1/text()',
        'description': '//section[@class="scene"]//p[not(@align="center")]/text()',
        'date': '//section[@class="scene"]/div/meta[@itemprop="datePublished"]/@content',
        'date_formats': ['%Y-%m-%d'],
        'image': '//section[@class="scene"]/div/meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//section[@class="scene"]//h2/text()',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '//section[@class="scene"]/div/meta[@itemprop="contentURL"]/@content',
        'pagination': '/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//section[@class="recent container"]/ul/li')
        for scene in scenes:
            image = scene.xpath('./a/figure/img/@src')
            if image:
                image = image.get()
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                image = base + image.strip()
            else:
                image = ''

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'imageback': image})

    def get_site(self, response):
        site = tldextract.extract(response.url).domain
        if site:
            site = match_site(site)
        return site

    def get_parent(self, response):
        site = tldextract.extract(response.url).domain
        if site:
            site = match_site(site)
        return site

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = trailer.get()
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                trailer = base + trailer.strip()
                return trailer.replace(" ", "%20")

        return ''

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = performers.get()
            performers = performers.split("|")
            performers2 = [x.strip() for x in performers]
            performers3 = [x for x in performers2 if x]
            return list(map(lambda x: x.strip(), performers3))

        return []

    def get_id(self, response):
        externid = super().get_id(response)
        return externid.lower()

    def get_image(self, response):
        image = super().get_image(response)
        if not image or re.search(r'/(p\d{1,2}\.jpg)', image):
            if response.meta['imageback']:
                return response.meta['imageback'].strip().replace(" ", "%20")
        return image

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = self.get_from_regex(date.get(), 're_date')

            if date:
                date = date.replace('Released:', '').replace('Added:', '').strip()
                date_formats = self.get_selector_map('date_formats') if 'date_formats' in self.get_selector_map() else None

                return self.parse_date(date, date_formats=date_formats).isoformat()
        if not date:
            return self.parse_date('today').isoformat()
