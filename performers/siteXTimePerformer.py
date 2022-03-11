import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteXTimePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="models"]/section/h1/text()',
        'image': '//div[@class="models"]/div[@class="model-img"]/img/@src',
        'birthday': '//div[@class="models"]/section/ul/li[contains(text(), "Date")]/span/text()',
        'haircolor': '//div[@class="models"]/section/ul/li[contains(text(), "Hair")]/span/text()',
        'astrology': '//div[@class="models"]/section/ul/li[contains(text(), "Zodiac")]/span/text()',
        'ethnicity': '//div[@class="models"]/section/ul/li[contains(text(), "Ethnicity")]/span/text()',
        'birthplace': '//div[@class="models"]/section/ul/li[contains(text(), "Birthplace")]/span/text()',
        'height': '//div[@class="models"]/section/ul/li[contains(text(), "Height")]/span/text()',
        'weight': '//div[@class="models"]/section/ul/li[contains(text(), "Weight")]/span/text()',
        'measurements': '//div[@class="models"]/section/ul/li[contains(text(), "Measurements")]/span/text()',
        'bio': '//div[@class="models"]/section/p/text()',
        'external_id': r'model\/(.*)/'
    }

    paginations = [
        '/?act=ListaPornostar&pageID=%s&cat=PORNOSTAR_INTERNAZIONALI',
        '/?act=ListaPornostar&pageID=%s&cat=PORNOSTAR_ITALIANE',
    ]

    name = 'XTimePerformer'
    network = 'XTime'

    url = 'http://xtime.tv'

    def start_requests(self):
        link = "http://xtime.tv/?act=Disclaimer&accept=1"
        yield scrapy.Request(link, callback=self.start_requests_2,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def start_requests_2(self, response):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination},
                                 headers=self.headers,
                                 cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_performers(self, response):
        performers = response.xpath('//li/div[@class="details"]/following-sibling::a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return 'Female'

    def get_height(self, response):
        height = super().get_height(response)
        height = re.search(r'(\d{2,3})', height)
        if height:
            height = height.group(1) + "cm"
        return height

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
