import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteToaxxxPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'ToaxxxPerformer'
    network = 'Toaxxx'

    def get_gender(self, response):
        return 'Female'

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        url = "https://www.toaxxx.com/modelspage/"
        yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href, "/tag/")]/..')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//font/b/text()')
            if name:
                name = name.get()
                if "(" in name:
                    name = re.search(r'(.*)\(', name).group(1)
            item['name'] = name.strip()
            item['image'] = performer.xpath('.//img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Female'
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
            item['network'] = 'Toaxxx'
            item['url'] = performer.xpath('.//a[contains(@href, "/tag/")]/@href').get()

            yield item
