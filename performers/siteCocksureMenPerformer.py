import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteCocksureMenPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/%s/latest/',
        'external_id': r'.*/(.*?)\.htm'
    }

    name = 'CocksureMenPerformer'
    network = 'Jake Cruise Media'

    start_urls = [
        'https://www.cocksuremen.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="sexyman_img"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./a//span/text()').get())
            item['image'] = self.format_link(response, "tour/" + performer.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Male'
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
            item['network'] = 'Jake Cruise Media'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
