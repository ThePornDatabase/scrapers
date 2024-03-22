import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteCombatZonePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'CombatZonePerformer'

    start_url = 'https://tour.combatzonexxx.com'

    paginations = [
        '/models/models_%s_d.html?g=f',
        '/models/models_%s_d.html?g=t',
    ]

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "item-portrait")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./div[1]/a/span/text()').get())
            image = performer.xpath('./div[1]//img/@src0_2x|./div[1]//img/@src0_1x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            if "g=t" in response.url:
                item['gender'] = "Trans Female"
            else:
                item['gender'] = "Female"
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
            item['network'] = 'Combat Zone'
            item['url'] = self.format_link(response, performer.xpath('./div[1]/a/@href').get())

            yield item
