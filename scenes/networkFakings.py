import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class FakingsSpider(BaseSceneScraper):
    name = 'Fakings'
    network = 'FA Kings'
    parent = 'FA Kings'

    start_urls = [
        'https://www.fakings.com'
    ]

    selector_map = {
        'title': '//h1//a/text()',
        'description': '//span[@class="grisoscuro"]/text()',
        'performers': '//strong[contains(., "Actr")]//following-sibling::a/text()',
        'tags': '//strong[contains(., "Categori")]//following-sibling::a/text()',
        'external_id': 'video/(.+)\.htm',
        'trailer': '',
        'pagination': '/en/buscar/%s.htm'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="zona-listado2"]')
        for scene in scenes:

            meta = {}

            date = scene.xpath('.//p[@class="txtmininfo calen sinlimite"]//text()').get().strip()
            meta['date'] = dateparser.parse(date,settings={'DATE_ORDER': 'DMY'}).isoformat()
            meta['image'] = scene.css('.bordeimagen::attr(src)').get()

            yield scrapy.Request(url=self.format_link(response, scene.css('a::attr(href)').get()), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return response.xpath('//strong[contains(., "Serie")]//following-sibling::a/text()').get().strip()
