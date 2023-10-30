import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteDawgpoundUSAPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/dawgz.cfm?PAGE=%s',
        'external_id': r'.*/(.*?)\.htm'
    }

    name = 'DawgpoundUSAPerformer'
    network = 'DawgpoundUSA'

    start_urls = [
        'https://dawgpoundusa.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "item")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h4/div/text()').get())
            item['image'] = self.format_link(response, performer.xpath('.//img/@src').get())
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
            item['network'] = 'DawgpoundUSA'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
