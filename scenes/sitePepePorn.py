import urllib.parse
import string
import dateparser
import scrapy
from googletrans import Translator
from tpdb.BaseSceneScraper import BaseSceneScraper


class FakingsSpider(BaseSceneScraper):
    name = 'PepePorn'
    network = 'FA Kings'
    parent = 'PepePorn'
    site = 'PepePorn'

    url = 'https://www.pepeporn.com'

    paginations = [
        '/videos/%s.htm'
    ]

    selector_map = {
        'title': '//h1//a/text()|//h1[@class="subtitle"]//text()',
        'description': '//span[@class="grisoscuro"]/text()',
        'performers': '//strong[contains(., "Actr")]//following-sibling::a/text()',
        'tags': '//strong[contains(., "Categori")]//following-sibling::a/text()',
        'external_id': 'video/(.+)\\.htm',
        'trailer': '',
        'pagination': '/videos/%s.htm'
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

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(set(performers))
        return performers

    def get_title(self, response):
        translator = Translator()
        title = super().get_title(response).lower()
        if title:
            title = translator.translate((title.lower()), src='es', dest='en')
            title = string.capwords(title.text)
        return title

    def get_description(self, response):
        translator = Translator()
        description = super().get_description(response)
        if description:
            description = translator.translate((description.strip()), src='es', dest='en')
            description = description.text.strip()
            return description
        return ''

    def get_tags(self, response):
        translator = Translator()
        tagsoriginal = super().get_tags(response)
        tags = []
        for tag in tagsoriginal:
            tag = translator.translate((tag.strip()), src='es', dest='en')
            tag = tag.text.strip()
            tags.append(tag)
        tags.append("Latina")
        tags.append("Latin American")
        return tags



