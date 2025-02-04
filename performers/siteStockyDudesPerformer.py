import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from urllib.parse import urlencode


class SiteStockyDudesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile"]//div[@class="main_title"]/h3/text()',
        'image': '//div[@class="profile"]//img[1]/@src',
        'bio': '//div[@class="frame"]//div[@id="profAbout"]/span/text()',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//div[@class="profile"]//ul/li[contains(text(), "Height")]'
        '/strong/text()',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//div[@class="profile"]//ul/li[contains(text(), "Weight")]'
        '/strong/text()',
        'pagination': '/models?Page=%s',
        'external_id': r'profile/(.*)/?$'
    }

    name = 'StockyDudesPerformer'
    network = 'Stocky Dudes'

    start_urls = [
        'https://www.stockydudes.com',
    ]

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0

        if 'pagingData' not in response.meta:
            response.meta['pagingData'] = self.get_pagin_data(response)

        for performer in performers:
            count += 1
            yield performer

        if count:
            if ('page' in response.meta and
               response.meta['page'] < self.limit_pages):
                meta = response.meta
                meta['page'] = meta['page'] + 1
                meta['pagingData']['from'] += count

                print('NEXT PAGE: ' + str(meta['page']))

                link = self.format_link(response, '/_ajaxLoadModels.php?' +
                                        urlencode(meta['pagingData']))
                self.headers['x-requested-with'] = 'XMLHttpRequest'

                yield scrapy.Request(url=link,
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        selector = response.selector

        if ('json' in response.headers.get('Content-Type').decode('utf-8')
                and 'html' in response.json()):
            selector = scrapy.Selector(text=response.json()['html'])
        
        performers = selector.xpath(
            '//div[@class="model_title"]//a/@href').getall()
        
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer),
                                 callback=self.parse_performer,
                                 cookies=self.cookies, headers=self.headers)

    def get_pagin_data(self, response):
        page_data = {}
        page_data['from'] = int(response.xpath(
            '//div[@id="modelsLoadMore"]/@data-from').get())
        page_data['filter'] = response.xpath(
            '//div[@id="modelsLoadMore"]/@data-filter').get()
        page_data['sort'] = response.xpath(
            '//div[@id="modelsLoadMore"]/@data-sort').get()
        page_data['_'] = '1212121'

        return page_data
