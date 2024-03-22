import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteLadyboyGoldPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="container"]/div[1]/div[2]/div[1]/text()',
        'image': '//div[@class="container"]//div[contains(@class,"photoUpdate-image")]//img/@src',
        'image_blob': True,
        'bio': '//div[@class="container"]//div[@class="profileBio"]/text()',
        'height': '//div[@class="container"]//li[contains(text(), "Height:")]/text()',
        're_height': r'(\d+cm)',
        'measurements': '//div[@class="container"]//li[contains(text(), "Measurements:")]/text()',
        're_measurements': r'(\d+\w+?-\d+-\d+)',
        'cupsize': '//div[@class="container"]//li[contains(text(), "Measurements:")]/text()',
        're_cupsize': r'(\d+\w+?)-\d+-\d+',
        'weight': '//div[@class="container"]//li[contains(text(), "Weight:")]/text()',
        're_weight': r'(\d+kg)',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'LadyboyGoldPerformer'
    network = 'Ladyboy Gold'

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = 'https://www.ladyboygold.com/index.php?section=1813'
        yield scrapy.Request(link, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_gender(self, response):
        return 'Trans Female'

    def get_performers(self, response):
        performers = response.xpath('//p[@class="setModel"]/a/@href').getall()
        for performer in performers:
            performer = re.search(r'(.*?)\&nats', performer).group(1)
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
