import urllib.parse
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class FakingsSpider(BaseSceneScraper):
    name = 'Fakings'
    network = 'FA Kings'

    url = 'https://www.fakings.com'

    paginations = [
        '/en/buscar/%s.htm?all',
        '/en/serie/ainaras-diary/%s.htm?all',
        '/en/serie/arnaldo-series/%s.htm?all',
        '/en/serie/behind-fakings/%s.htm?all',
        '/en/serie/big-rubber-cocks/%s.htm?all',
        '/en/serie/blind-date/%s.htm?all',
        '/en/serie/blowjob-lessons/%s.htm?all',
        '/en/serie/busted/%s.htm?all',
        '/en/serie/curvy-girls/%s.htm?all',
        '/en/serie/exchange-student-girls/%s.htm?all',
        '/en/serie/fakings-academy/%s.htm?all',
        '/en/serie/fakings-castings/%s.htm?all',
        '/en/serie/fakings-pornstars/%s.htm?all',
        '/en/serie/fakings-slutwalk/%s.htm?all',
        '/en/serie/fakingsvr/%s.htm?all',
        '/en/serie/fakins-wild-party/%s.htm?all',
        '/en/serie/first-fakings/%s.htm?all',
        '/en/serie/free-couples/%s.htm?all',
        '/en/serie/free-pussy-day/%s.htm?all',
        '/en/serie/fuck-me-fool/%s.htm?all',
        '/en/serie/fuck-them/%s.htm?all',
        '/en/serie/horsedicks/%s.htm?all',
        '/en/serie/i-sell-my-girlfriend/%s.htm?all',
        '/en/serie/im-a-webcam-girl/%s.htm?all',
        '/en/serie/innocent-18/%s.htm?all',
        '/en/serie/ivan-amor/%s.htm?all',
        '/en/serie/la-porno-house/%s.htm?all',
        '/en/serie/loverfans/%s.htm?all',
        '/en/serie/milf-club/%s.htm?all',
        '/en/serie/my-first-anal/%s.htm?all',
        '/en/serie/my-first-dp/%s.htm?all',
        '/en/serie/nerd-buster/%s.htm?all',
        '/en/serie/newbies-or-so-they-say-/%s.htm?all',
        '/en/serie/next-door-girl/%s.htm?all',
        '/en/serie/parejasnet/%s.htm?all',
        '/en/serie/perverting-couples/%s.htm?all',
        '/en/serie/quarantine-stories/%s.htm?all',
        '/en/serie/sick-videos/%s.htm?all',
        '/en/serie/swingers-life/%s.htm?all',
        '/en/serie/talk-to-them/%s.htm?all',
        '/en/serie/the-anatomical-sulphate/%s.htm?all',
        '/en/serie/the-naughty-bet/%s.htm?all',
        '/en/serie/trans-fakings/%s.htm?all',
        '/en/serie/very-voyeur/%s.htm?all',
    ]

    selector_map = {
        'title': '//h1//a/text()|//h1[@class="subtitle"]//text()',
        'description': '//span[@class="grisoscuro"]/text()',
        'performers': '//strong[contains(., "Actr")]//following-sibling::a/text()',
        'tags': '//strong[contains(., "Categori")]//following-sibling::a/text()',
        'external_id': 'video/(.+)\\.htm',
        'trailer': '',
        'pagination': '/en/buscar/%s.htm?all'
    }

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
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
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="zona-listado2"]')
        for scene in scenes:

            meta = {}

            date = scene.xpath('.//p[@class="txtmininfo calen sinlimite"]//text()').get().strip()
            meta['date'] = dateparser.parse(
                date, settings={'DATE_ORDER': 'DMY'}).isoformat()
            meta['image'] = scene.xpath('./div[@class="zonaimagen"]/a/img/@src').get()
            meta['image'] = urllib.parse.quote_plus(meta['image'])
            meta['image'] = meta['image'].replace('%2F', '/').replace('%3A', ':')
            meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            yield scrapy.Request(url=self.format_link(response, scene.css('a::attr(href)').get()), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//strong[contains(., "Serie")]//following-sibling::a/text()')
        if site:
            site = site.get()
        else:
            site = "FaKings"
        return site.strip()

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(set(performers))
        return performers
