import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//img[contains(@class, "detail__picture")]/@src',
        'image_blob': True,
        'birthday': '//div[contains(@class, "pornstar-detail__description-block")]//strong[contains(text(), "Birthday")]/following-sibling::text()[1]',
        're_birthday': r'(\w+ \d{1,2}, \d{4})',
        'height': '//div[contains(@class, "pornstar-detail__description-block")]//strong[contains(text(), "Height")]/following-sibling::text()[1]',
        're_height': r'(\d+ cm)',
        'measurements': '//div[contains(@class, "pornstar-detail__description-block")]//strong[contains(text(), "Measurements")]/following-sibling::text()[1]',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'EnjoyxPerformer'
    network = "Enjoyx"

    start_url = 'https://enjoyx.com'

    paginations = [
        '/model/girls?page=%s',
        '/model/boys?page=%s',
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class, "pornstar-card")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def get_gender(self, response):
        if "girls" in response.meta['pagination']:
            return "Female"
        if "boys" in response.meta['pagination']:
            return "Male"

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            return cupsize.strip()
        else:
            if 'measurements' in self.selector_map:
                measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''
