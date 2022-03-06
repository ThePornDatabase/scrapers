# This is essentially a filler scraper from an index site.  These are the
# sites that currently aren't being scraped on TPDB from other scrapers
import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkFilthFlixSpider(BaseSceneScraper):
    name = 'FilthFlix'

    start_urls = [
        ['https://filthflix.com', '/channels/foot-fuckers/page-%s/', 'Foot Fuckers'],
        ['https://filthflix.com', '/channels/german-castings/page-%s/', 'German Castings'],
        ['https://filthflix.com', '/channels/hotelust/page-%s/', 'Hotelust'],
        ['https://filthflix.com', '/channels/hq-porno/page-%s/', 'HQ-Porno'],
        ['https://filthflix.com', '/channels/julie-skyhigh/page-%s/', 'Julie Skyhigh'],
        ['https://filthflix.com', '/channels/katiek-official/page-%s/', 'Katie K'],
        ['https://filthflix.com', '/channels/pure-beauties/page-%s/', 'Pure Beauties'],
        ['https://filthflix.com', '/channels/pussy-forever/page-%s/', 'Pussy Forever'],
        ['https://filthflix.com', '/channels/russian-teen-tryouts/page-%s/', 'Russian Teen Tryouts'],
        ['https://filthflix.com', '/channels/spanish-sluts/page-%s/', 'Spanish Sluts'],
        ['https://filthflix.com', '/channels/summer-hookups/page-%s/', 'Summer Hookups'],
        ['https://filthflix.com', '/channels/trashy-teens/page-%s/', 'Trashy Teens'],
        ['https://filthflix.com', '/channels/viva-la-france/page-%s/', 'Viva La France'],
        ['https://filthflix.com', '/channels/voyeur-hunter/page-%s/', 'Voyeur Hunter'],
    ]

    selector_map = {
        'title': '//h2[@class="video__headline"]/text()',
        'description': '//div[@class="video__description"]/p[contains(@class, "video__text")]/text()',
        'date': '//strong[contains(text(), "Published")]/following-sibling::text()',
        'date_formats': ['%d %b %Y'],
        'image': '//div[@class="video__player"]/img/@src|//div[@class="video__player"]//video/@poster',
        'performers': '//strong[contains(text(), "Models")]/following-sibling::a/text()',
        'tags': '//strong[contains(text(), "Tags")]/following-sibling::a[contains(@href, "/movies/")]/text()',
        'external_id': r'movies/(.*)$',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):
        for link in self.start_urls:
            base = link[0]
            pagination = link[1]
            site = link[2]
            yield scrapy.Request(url=self.get_next_page_url(base, pagination, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'site': site, 'pagination': pagination, 'base': base},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['base'], meta['pagination'], meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, pagination, page):
        url = (base + pagination) % page
        return url

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class, "video-grid__item")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        if self.get_selector_map('description'):
            description_xpath = self.process_xpath(response, self.get_selector_map('description'))
            if description_xpath:
                description = description_xpath.get()
                if description:
                    return self.cleanup_description(description)
        return ''

    def get_parent(self, response):
        return response.meta['site']

    def get_site(self, response):
        return response.meta['site']

    def get_network(self, response):
        return 'FilthFlix'
