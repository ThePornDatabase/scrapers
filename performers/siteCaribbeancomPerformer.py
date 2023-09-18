import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteCaribbeancomPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/%s/',
        'external_id': r'model/(.*)/'
    }

    name = 'CaribbeancomPerformer'
    network = 'Caribbeancom'

    start_urls = [
        'https://en.caribbeancom.com',
    ]

    def start_requests(self):
        orig_link = 'https://en.caribbeancom.com/eng/actress/%s.html'
        for c in list(string.ascii_lowercase):
            link = orig_link % c
            yield scrapy.Request(link, callback=self.get_performers)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[@class="meta-name"]/text()').get())
            item['name'] = re.sub(' +', ' ', item['name'])
            if "&" not in item['name'].lower() and "," not in item['name'].lower() and "and" not in item['name'].lower():
                item['image'] = self.format_link(response, performer.xpath('.//img/@src').get())
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
                item['network'] = 'Caribbeancom'
                item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

                yield item
