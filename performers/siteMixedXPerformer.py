import re
import dateparser
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteMixedXPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[contains(text(),"About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'astrology': '//strong[contains(text(),"Sign")]/following-sibling::text()',
        'eyecolor': '//strong[contains(text(),"Eye")]/following-sibling::text()',
        'birthday': '//strong[contains(text(),"Birthday")]/following-sibling::text()',
        'bio': '//div[@class="profile-about"]/p/text()',
        'external_id': r'models/(.*).html'
    }

    url = 'https://mixedx.com/'

    paginations = {
        '/models/%s/latest/?g=f',
        '/models/%s/latest/?g=m',
    }

    name = 'MixedXPerformer'
    network = "Mixed X"

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={
                'page': self.page, 'pagination': pagination},
                headers=self.headers,
                cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
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
                        yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                             callback=self.parse,
                                             meta=meta,
                                             headers=self.headers,
                                             cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = name.replace("About", "").strip()
        return name

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class,"item-portrait")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta=meta
            )

    def get_gender(self, response):
        meta = response.meta
        if 'g=m' in meta['pagination']:
            return "Male"
        return "Female"

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements)
                if measurements:
                    measurements = measurements.group(1)
                    measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if cupsize:
                cupsize = re.search(r'(\d+\w+)-\d+-\d+', cupsize)
                if cupsize:
                    cupsize = cupsize.group(1)
                    return cupsize.strip().upper()
        return ''

    def get_bio(self, response):
        bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
        if bio:
            bio = " ".join(bio)
            return bio

        return ''

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            return dateparser.parse(date.strip(), settings={'TIMEZONE': 'UTC'}).isoformat()
        return None
