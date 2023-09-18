import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SiteYoungBastardsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/?models/%s',
        'external_id': r'model/(.*)/'
    }

    name = 'YoungBastardsPerformer'
    network = 'Young Bastards'

    start_urls = [
        'https://youngbastards.com',
    ]

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="itemm"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[@class="nm-name"]/text()').get())
            item['image'] = performer.xpath('./a/img/@src').get()
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
            item['network'] = 'Young Bastards'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
