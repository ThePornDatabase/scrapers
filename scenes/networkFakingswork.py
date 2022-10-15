import urllib.parse
import dateparser
import scrapy
from scrapy import FormRequest

from tpdb.BaseSceneScraper import BaseSceneScraper


class FakingsWorkSpider(BaseSceneScraper):
    name = 'FakingsWork'
    network = 'FA Kings'

    start_urls = [
        'https://www.fakings.com'
    ]

    selector_map = {
        'title': '//h1//a/text()|//h1[@class="subtitle"]//text()',
        'description': '//span[@class="grisoscuro"]/text()',
        'performers': '//strong[contains(., "Actr")]//following-sibling::a/text()',
        'tags': '//strong[contains(., "Categori")]//following-sibling::a/text()',
        'external_id': 'video/(.+)\\.htm',
        'trailer': '',
        'pagination': '/en/buscar/%s.htm'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield FormRequest(url=self.get_next_page_url(link, self.page),
                                 formdata={'all': ''},
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response):
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
                yield FormRequest(url=self.get_next_page_url(response.url, meta['page']),
                                     formdata={'all': ''},
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="zona-listado2"]')
        for scene in scenes:

            meta = {}

            date = scene.xpath(
                './/p[@class="txtmininfo calen sinlimite"]//text()').get().strip()
            meta['date'] = dateparser.parse(
                date, settings={'DATE_ORDER': 'DMY'}).isoformat()
            meta['image'] = scene.css('.bordeimagen::attr(src)').get()
            meta['image'] = urllib.parse.quote_plus(meta['image'])
            meta['image'] = meta['image'].replace('%2F', '/').replace('%3A', ':')
            # ~ meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            meta['image_blob'] = ''

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
