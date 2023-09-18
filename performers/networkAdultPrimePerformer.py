import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//span[@class="active-crumb"]/text()',
        'image': '//div[@class="ratio-square"]/@style',
        're_image': r'url\((http.*?)\)',
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//span[contains(text(), "Eye color")]/text()',
        're_eyecolor': r'color: (.*)',
        'fakeboobs': '',
        'haircolor': '//span[contains(text(), "Hair color")]/text()',
        're_haircolor': r'color: (.*)',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    paginations = {
            '/performers?sort=createdAt%20DESC&gender=female&page=<PAGE>',
            '/performers?sort=createdAt%20DESC&gender=male&page=<PAGE>',
            '/performers?sort=createdAt%20DESC&gender=trans&page=<PAGE>',
    }

    name = 'AdultPrimePerformer'
    network = 'Adult Prime'

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = 'https://adultprime.com'
        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        pagination = pagination.replace("<PAGE>", str(page))
        return self.format_url(base, pagination)

    def get_gender(self, response):
        meta = response.meta
        return string.capwords(re.search(r'gender=(.*?)\&', meta['pagination']).group(1))

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class, "performer-wrapper")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)
