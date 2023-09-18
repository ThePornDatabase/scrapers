import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SiteGuysInSweatpantsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'GuysInSweatpantsPerformer'
    network = 'Guys In Sweatpants'

    cookies = {"pp-accepted": "true"}

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        url = "https://guysinsweatpants.com/models"
        yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//li[contains(@class, "gallery-item-1")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[@class="title"]/text()').get())
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
            item['network'] = 'Guys In Sweatpants'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
