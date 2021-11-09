import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


def get_birthday_from_age(age):
    age = int(age.strip())
    if 18 <= age <= 99:
        birthdate = datetime.now() - relativedelta(years=age)
        birthdate = birthdate.strftime('%Y-%m-%d')
        return birthdate
    return ''


class VegasDreamworksPerformerSpider(BasePerformerScraper):
    name = 'VegasDreamworksPerformer'
    network = 'Vegas Dreamworks'
    parent = 'Vegas Dreamworks'

    start_urls = [
        ['https://screwmetoo.com/', '/models/page/%s/?sortby=date'],
        ['https://milftrip.com/', '/models/page/%s/?sortby=date'],
        ['https://tuktukpatrol.com/', '/models/page/%s/?sortby=date'],
        ['https://helloladyboy.com/', '/shemale-models/page/%s/?sortby=date'],
        ['https://trikepatrol.com/', '/models/page/%s/?sortby=date'],
    ]

    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="model-contr"]//amp-img/@src',
        'birthday': '//span[contains(text(),"Age")]/following-sibling::text()',
        'measurements': '//span[contains(text(),"Measurements")]/following-sibling::text()',
        'cupsize': '//span[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//span[contains(text(),"Height")]/following-sibling::text()',
        'weight': '//span[contains(text(),"Weight")]/following-sibling::text()',
        'haircolor': '//span[contains(text(),"Hair Color")]/following-sibling::text()',
        'eyecolor': '//span[contains(text(),"Eye Color")]/following-sibling::text()',
        'bio': '//div[@class="model-desc"]/p/text()',
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
        performers = response.xpath('//a[contains(@href,"/model/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                if re.search('(.*?)-.*-.*', cupsize):
                    cupsize = re.search('(.*?)-.*-.*', cupsize).group(1)
                    if cupsize:
                        return cupsize.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                if re.search('(.*?)-.*-.*', measurements):
                    return measurements.strip()
        return ''

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            if bio:
                bio = " ".join(bio)
            else:
                bio = response.xpath('//div[@class="model-desc"]/text()').getall()
                if bio:
                    bio = " ".join(bio)
            return bio.strip()
        return ''

    def get_gender(self, response):
        if "helloladyboy" in response.url:
            return "Trans"
        return "Female"

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                if birthday.strip().isdigit():
                    age = birthday.strip()
                    birthday = get_birthday_from_age(age)
                    return birthday
        return ''
