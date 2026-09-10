import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
import tldextract
import dateparser


def match_site(argument):
    match = {
        'hardtied': "Hard Tied",
        'infernalrestraints': "Infernal Restraints",
        'realtimebondage': "Real Time Bondage",
        'sexuallybroken': "Sexually Broken",
        'topgrl': "Topgrl",
    }
    return match.get(argument, '')


INSEX = 'https://www.insex.com'
INSEX_BASE = 'https://www.insex.com/is/'

INSEX_DOMAINS = [
    'hardtied.com',
    'infernalrestraints.com',
    'realtimebondage.com',
    'sexuallybroken.com',
    'topgrl.com',
]

INSEX_START_URLS_FULL = [
    [INSEX, '/is/home.php?p=%%s&s=&d=%s&o=oldest' % d, INSEX_BASE, d] for d in INSEX_DOMAINS
]

INSEX_START_URLS_UPDATE = [
    [INSEX, '/is/home.php?p=%%s&s=&d=%s&o=newest' % d, INSEX_BASE, d] for d in INSEX_DOMAINS
]


class InsexSitesSpider(BaseSceneScraper):
    name = 'InsexSites'
    network = "Insex Network"
    parent = "Insex Network"

    # The network consolidated onto insex.com: the per-domain /ht/, /ir/, /rtb/,
    # /sb/ and /tg/ paths are gone and every site is served from
    # /is/home.php?d=<domain>, so the sites are still individually addressable.
    # Two cookies are needed -- 'consent' alone leaves the listing an empty shell;
    # 'verified' is what the agechecker.net popup sets and without it the page
    # renders navigation only.
    cookies = {'verified': 'true', 'consent': 'yes', 'dig': 'dig-intersec'}



    # Note: The primary index page at insexondemand.com doesn't have all of the releases listed.
    #       Also, the individual site pages seem to have a bug.  If you go in normal order, when you reach
    #       past xx pages the results start to become randomized.  (doesn't seem intentional, seems a coding
    #       error)
    #
    #       This bug doesn't seem to happen if you go in Oldest -> Newest order (for example, SB gave an extra 300 or
    #       so results going in reverse order)
    #
    #       Because of that, I put in an '-a full=true' flag which when used in combination with '-a limit_pages=all'
    #       will use the reverse date order and do a full import.

    start_urls_full = INSEX_START_URLS_FULL
    start_urls_update = INSEX_START_URLS_UPDATE

    selector_map = {
        'title': '//div[contains(@class, "has-text-weight-bold")]/text()',
        'description': '//div[contains(@class, "has-text-white-ter")][3]/text()',
        'date': '//div[@class="is-size-6 has-text-white-ter"]/span[@class="tag is-dark"]/text()',
        'image': '//video-js[1]/@poster',
        'performers': '//div[contains(@class, "has-text-white-ter")][1]//a[contains(@class, "is-dark")][position() < last()]/text() | //a[@class="tag is-dark" and contains(@href,"home.php?s=")]/text()',
        # ~ 'tags': '//div[@class="is-size-6 has-text-white-ter"]/span/text()',
        'tags': '',  # Tags removed due to how badly they suck at using tags
        'external_id': 'play.php\\?id\\=(\\w+)',
        'trailer': '//video-js[1]//source/@src',
        'pagination': ''
    }

    async def start(self):
        if hasattr(self, 'full') and self.full:
            links = self.start_urls_full
            print('Using reverse date order for full import')
        else:
            links = self.start_urls_update
            print('Using standard date order for latest updates')

        for link in links:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1], 'baseurl': link[2],
                                       'sitedomain': link[3]},
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
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//figure/a[contains(@href,"play.php")]/@href').getall()
        for scene in scenes:
            if meta['baseurl']:
                scene = meta['baseurl'] + scene.strip()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        """Every page is served from insex.com now, so the response URL no longer
        identifies the site -- it comes from the d= parameter the listing was
        requested with, falling back to the slug the scene page prints as a tag."""
        domain = response.meta.get('sitedomain') or ''
        site = match_site(domain.replace('.com', ''))
        if not site:
            for tag in response.xpath('//span[@class="tag is-dark"]/text()').getall():
                site = match_site(tag.strip().lower())
                if site:
                    break
        if not site:
            site = match_site(tldextract.extract(response.url).domain)
        return site

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        date.replace('Released:', '').replace('Added:', '').strip()
        return dateparser.parse(date.strip()).isoformat()

    # ~ def get_tags(self, response):
    # ~ if self.get_selector_map('tags'):
    # ~ tags = self.process_xpath(response, self.get_selector_map('tags')).getall()
    # ~ for tag in tags:
    # ~ if re.search(r'\d{4}-\d{2}-\d{2}', tag):
    # ~ tags.remove(tag)
    # ~ if tags:
    # ~ return list(map(lambda x: x.replace(u'\xa0', u' ').replace("&nbsp;", " ").strip().title(), tags))
    # ~ return []

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//div[@class="columns is-multiline"]/div/div/div/img/@src').get()

        if image:
            return self.format_link(response, image)
        return ''

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = trailer.replace('\n', '').replace('\t', '').strip()
            if trailer:
                return trailer
        return ''
