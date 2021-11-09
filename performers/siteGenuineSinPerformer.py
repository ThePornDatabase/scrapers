import html
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteGenuineSinPerformerSpider(BasePerformerScraper):
    selector_map = {
        'external_id': 'girls/(.+)/?$'
    }

    url = 'http://genuinesin.com/'

    paginations = {
        '/models/%s/latest/?g=f',
        '/models/%s/latest/?g=m',
    }

    name = 'GenuineSinPerformer'
    network = "Genuine Sin"

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

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="item-portrait"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//h4/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('./a/img/@src0_1x').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a[1]/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'Genuine Sin'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            if 'g=m' in meta['pagination']:
                item['gender'] = "Male"
            else:
                item['gender'] = "Female"

            yield item
