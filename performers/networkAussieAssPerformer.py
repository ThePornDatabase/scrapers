import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class AussieAssPerformerSpider(BasePerformerScraper):
    name = 'AussieAssPerformer'
    network = 'Aussie Ass'
    parent = 'Aussie Ass'

    start_urls = [
        ['https://aussiepov.com/', '/sets.php?page=%s&s=d'],
        ['https://aussieass.com/', '/models/models_%s_d.html'],
    ]

    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="row"]/div/img/@src0_1x',
        'cupsize': '//ul[@class="description"]/text()[contains(.,"cup size")]/following-sibling::span[1]/text()',
        'astrology': '//ul[@class="description"]/text()[contains(.,"star sign")]/following-sibling::span[1]/text()',
        'height': '//ul[@class="description"]/text()[contains(.,"height")]/following-sibling::span[1]/text()',
        'pagination': '/girls/page-%s/?tag=&sort=recent&pussy=&site=',
        'external_id': 'girls/(.+)/?$'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if not hasattr(self, 'get_performers'):
            raise AttributeError('get_performers function missing')

        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count and response.meta['page'] < 10:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                url = self.get_next_page_url(response.url, meta['page'], pagination)
                yield scrapy.Request(url,
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        page_link = pagination % page
        return self.format_url(base, page_link)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="box"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                cupsize = cupsize.split()[0]
                return cupsize
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height:
                    height = re.sub(r'\s+', '', height)
                    height = re.search(r'(\d+cm)', height)
                    if height:
                        height = height.group(1)
                        return height.strip()
        return ''

    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology')).get()
            if astrology:
                astrology = astrology.split()[0]
                return astrology
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if "aussieass" in response.url:
                image = "https://aussieass.com" + image
            if "aussiepov" in response.url:
                image = "https://aussiepov.com" + image
            if image:
                return image.strip()
        return None
