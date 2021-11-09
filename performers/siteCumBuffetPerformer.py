import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteCumBuffetPerformerSpider(BasePerformerScraper):
    name = 'CumBuffetPerformer'
    network = 'Cum Buffet'

    start_urls = {
        'https://www.cumbuffet.com/',
    }

    selector_map = {
        'name': '//h1[@class="mt"]/span/text()',
        'image': '//div[@class="profile-img"]/img/@src',
        'measurements': '//div[@class="profile-info"]/ul/li/b[contains(text(),"Measurements")]/following-sibling::text()',
        'bio': '//div[@class="description"]/text()',
        'pagination': '',
        'external_id': 'girls/(.+)/?$'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url="https://www.cumbuffet.com/girls",
                                 callback=self.get_performers,
                                 meta={'page': self.page, 'pagination': link[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="girl"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

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

    def get_gender(self, response):
        return "Female"
