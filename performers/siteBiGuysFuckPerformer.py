import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteBiGuysFuckPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title"]//h1//text()',
        'image': '//div[@class="about-models-left"]/img/@src',
        'cupsize': '//div[@class="value-holder"]/div[@class="details"]/span[contains(text(),"breast size")]/../../div[@class="characteristics"]/span/text()',
        'height': '//div[@class="value-holder"]/div[@class="details"]/span[contains(text(),"height")]/../../div[@class="characteristics"]/span/text()',
        'weight': '//div[@class="value-holder"]/div[@class="details"]/span[contains(text(),"weight")]/../../div[@class="characteristics"]/span/text()',
        'bio': '//div[@class="content"]/p/text()',
        'pagination': '/models?page=%s',
        'external_id': 'models\/(.*).html'
    }

    name = 'BiGuysFuckPerformer'
    network = 'Bi Guys Fuck'
    parent = 'Bi Guys Fuck'

    url = 'https://www.biguysfuck.com'

    paginations = [
        '/models/females?page=%s',
        '/models/males?page=%s'
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
        performers = response.xpath('//div[@class="modelsColumn"]/a/@href').getall()
        for performer in performers:
            if "females" in response.url:
                gender = "Female"
            else:
                gender = "Male"
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'gender': gender}
            )

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).getall()
        name = list(map(lambda x: x.strip().title(), name))
        name = " ".join(name)
        return name.strip()


