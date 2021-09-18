import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteWhoaBoyzPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "description")]/h2/comment()/following-sibling::text()',
        'image': '//div[@class="container"]/div[contains(@class, "g-2")]//img/@src0_2x',
        'height': '//p[@class="model-description-info"]//text()[contains(., "Height")]',
        'weight': '//p[@class="model-description-info"]//text()[contains(., "Weight")]',
        'measurements': '//p[@class="model-description-info"]//text()[contains(., "Measurements")]',
        'bio': '//p[@class="model-description-info"]/following-sibling::comment()[contains(., "Bio Extra Field")]/following-sibling::text()[1]',
        'pagination': '/tour/models/models_%s.html?g=f',
        'external_id': r'models\/(.*).html'
    }

    name = 'WhoaBoyzPerformer'
    network = "Whoa Boyz"

    url = 'https://www.whoaboyz.com'

    paginations = [
        '/tour/models/models_%s.html?g=f',
        '/tour/models/models_%s.html?g=m',
    ]

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={
                'page': self.page, 'pagination': pagination},
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
        performers = response.xpath('//div[@class="preview"]/a/@href').getall()
        for performer in performers:
            if "g=m" in response.url:
                gender = "Male"
            else:
                gender = "Female"
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta={'gender': gender})

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'(\d{2,3})', weight)
        if weight:
            weight = weight.group(1)
            weight = str(round(int(weight) * .45359237)) + "kg"
            return weight
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        height = re.search(r'(\d).*?(\d{1,2})', height)
        if height:
            feet = int(height.group(1))
            inches = int(height.group(2))
            cm = round((inches + (feet * 12)) * 2.54)
            return str(cm) + "cm"
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                if re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                    measurements = re.sub(r'[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements'))
            if cupsize:
                cupsize = cupsize.get()
                if re.search(r'(\d+\w+)-\d+-\d+', cupsize):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', cupsize).group(1)
                    if cupsize:
                        return cupsize.strip().upper()
        return ''
