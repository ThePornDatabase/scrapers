import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteChristianWildePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'ChristianWildePerformer'

    start_url = 'https://christianwilde.com'

    paginations = [
        '/models/models_%s.html?g=m',
        '/models/models_%s.html?g=f',
        '/models/models_%s.html?g=tf',
        '/models/models_%s.html?g=tm',
        '/models/models_%s.html?g=nb',
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
                print('NEXT PAGE: ' + str(meta['pagination']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//p/a/text()').get())
            image = performer.xpath('.//img/@src0_3x|.//img/@src0_2x|.//img/@src0_1x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            item['gender'] = 'Male'
            if "g=f" in response.url:
                item['gender'] = 'Female'
            if "g=m" in response.url:
                item['gender'] = 'Male'
            if "g=tf" in response.url:
                item['gender'] = 'Trans Female'
            if "g=tm" in response.url:
                item['gender'] = 'Trans Male'
            if "g=nb" in response.url:
                item['gender'] = 'Non Binary'
            item['astrology'] = ''
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
            item['network'] = 'Christian Wilde'
            item['url'] = self.format_link(response, performer.xpath('.//p/a/@href').get())

            yield item
