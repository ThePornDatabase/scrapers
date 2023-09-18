import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SiteXXXJobInterviewsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars/page%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'XXXJobInterviewsPerformer'
    network = 'XXX Job Interviews'

    start_urls = [
        'https://xxxjobinterviews.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="girls-item"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[@class="description"]/text()').get())
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
            item['network'] = 'XXX Job Interviews'
            item['url'] = self.format_link(response, performer.xpath('./div[1]/a/@href').get())

            yield item
