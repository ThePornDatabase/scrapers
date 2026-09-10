import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkCJXXXSpider(BaseSceneScraper):
    name = 'CJXXX'
    network = 'CJXXX'

    # Every tour is served from tour.<domain>; the apex only 302s there, and on
    # doctortwink.com that redirect is malformed ("https://tour.doctortwink.comvideos.php")
    # so the tour host is used directly everywhere.
    #
    # younglatinostudz.com is deliberately absent: its tour answers with a 133-byte
    # blank page carrying no videos at all.
    sites = {
        '80gays.com': '80 Gays',
        'asiaboy.net': 'Asia Boy',
        'asiantwinknetwork.com': 'Asian Twink Network',
        'auntiebob.com': "Auntie Bob",
        'barebackeu.com': 'Bareback EU',
        'barebacklatinoz.com': 'Bareback Latinoz',
        'barebackmedaddy.com': 'Bareback Me Daddy',
        'barebacktwinkz.com': 'Bare Back Twinkz',
        'brazilianstudz.com': 'Brazilian Studz',
        'cjxxx.com': 'CJXXX',
        'daddysasians.com': "Daddy's Asians",
        'defiantboyz.com': 'Defiant Boyz',
        'doctortwink.com': 'Doctor Twink',
        'gayamateurpass.com': 'Gay Amateur Pass',
        'gayasiancamz.com': 'Gay Asian Camz',
        'gayasianpiss.com': 'Gay Asian Piss',
        'gayasiantwinkz.com': 'Gay Asian Twinkz',
        'gaybarebackpass.com': 'Gay Bareback Pass',
        'gaylatinpass.com': 'Gay Latin Pass',
        'gaytwinkcamz.com': 'Gay Twink Camz',
        'germancumpigz.com': 'GermanCumPigz',
        'gloryholehookups.com': 'GloryHole HookUps',
        'hammerboysxxx.com': 'Hammer Boys XXX',
        'hotboyusa.com': 'Hot Boy USA',
        'iomacho.com': 'IO Macho',
        'laughingasians.com': 'Laughing Asians',
        'otbboyz.com': 'OTB Boyz',
        'pragueboyz.com': 'Prague Boyz',
        'ramjetvideo.com': 'Ram Jet Video',
        'spunkstarz.com': 'Spunk Starz',
        'str8boyzseduced.com': 'Str8 Boyz Seduced',
        'topherphoenix.com': 'Topher Phoenix',
        'twinkboysparty.com': 'Twink Boys Party',
        'twinkyfeet.com': 'Twinky Feet',
        'victorcodyxxx.com': 'Victor Cody XXX',
        'workinmenxxx.com': 'Workin Men XXX',
    }

    start_urls = ['https://tour.%s' % domain for domain in sorted(sites)]

    selector_map = {
        'title': '//span[@class="video_title"]/text()',
        # The tour publishes no dates at all - no meta, no visible text, nothing
        # in the markup - so TPDB falls back to the import date.
        'date': '',
        'description': '//div[contains(@class, "intro-video")]//p[not(@class)]/text()',
        'image': '//img[contains(@src, "/images/posts/")]/@src',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'id=(\d+)',
        # /videos.php is the whole catalogue - 25 to 80 cards depending on the
        # site, with no pagination links and no page/start parameter that does
        # anything. The page number is still interpolated because the base class
        # builds even the first request through this format string, but parse()
        # below never asks for a second page.
        'pagination': '/videos.php?page=%s',
        'type': 'Scene',
    }

    def parse(self, response, **kwargs):
        # Paginating would just re-request the same listing, so the base class'
        # pagination is deliberately not used.
        for scene in self.get_scenes(response):
            yield scene

    def get_scenes(self, response):
        for link in dict.fromkeys(response.xpath('//div[@class="videoSec"]//a/@href').getall()):
            if re.search(r'single-network-video\.php', link):
                yield scrapy.Request(url=self.format_link(response, link),
                                     callback=self.parse_scene, meta=response.meta)

    def get_id(self, response):
        # Scene ids restart at 1 on every site in the network, so the bare id is
        # not unique. Prefixing the domain keeps them apart.
        sceneid = super().get_id(response)
        return '%s-%s' % (self.get_domain(response), sceneid) if sceneid else ''

    @staticmethod
    def get_domain(response):
        return re.sub(r'^(?:www|tour)\.', '', response.url.split('/')[2]).lower()

    def get_site(self, response):
        domain = self.get_domain(response)
        return self.sites.get(domain, domain)

    def get_parent(self, response):
        return self.get_site(response)

    def get_tags(self, response):
        # The tour publishes no tags at all - But is a Gay network, so return a single tag for all scenes.
        return ["Gay"]